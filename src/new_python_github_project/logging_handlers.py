"""Custom logging handlers for the application.

This module provides specialized logging handlers to support the application's
dual-logging architecture:

1. BufferHandler: Captures pre-fork log messages for later replay in the GUI
2. GuiLogHandler: Routes log messages to the GUI terminal area (A3)

The handlers work together to ensure all log messages are visible both in the
terminal (during startup) and in the GUI (after daemonization).
"""

import logging
import tempfile
import os
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .main_window import MainWindow
from PyQt6.QtCore import QObject, pyqtSignal


class BufferHandler(logging.Handler):
    """Logging handler that buffers messages to a file for later retrieval.

    This handler is used to capture log messages that occur before the application
    daemonizes. These messages are then replayed in the GUI terminal after the
    application starts, ensuring users see the complete startup sequence.

    Uses a temporary file to store messages so they survive the fork/daemon process.
    """

    def __init__(self, level: int = logging.NOTSET) -> None:
        """Initialize the buffer handler.

        :param level: Minimum log level to handle
        :type level: int
        """
        super().__init__(level)
        # Check if we have an existing buffer file path (post-fork)
        existing_path = os.environ.get("LOGGING_BUFFER_FILE")
        if existing_path and os.path.exists(existing_path):
            self.buffer_file_path = existing_path
        else:
            # Create a new temporary file (pre-fork)
            self.buffer_file = tempfile.NamedTemporaryFile(
                mode="w+", delete=False, suffix=".log"
            )
            self.buffer_file_path = self.buffer_file.name
            self.buffer_file.close()
            # Store the path in environment variable for post-fork access
            os.environ["LOGGING_BUFFER_FILE"] = self.buffer_file_path

    def emit(self, record: logging.LogRecord) -> None:
        """Format and store a log record in the buffer file.

        :param record: The log record to buffer
        :type record: logging.LogRecord
        """
        try:
            message = self.format(record)
            # Append message to buffer file
            with open(self.buffer_file_path, "a") as f:
                f.write(message + "\n")
        except Exception:
            self.handleError(record)

    def get_messages(self) -> List[str]:
        """Get all buffered messages from the file.

        :return: List of formatted log messages
        :rtype: List[str]
        """
        try:
            if os.path.exists(self.buffer_file_path):
                with open(self.buffer_file_path, "r") as f:
                    messages = [line.rstrip("\n") for line in f.readlines()]
                return messages
            return []
        except Exception:
            return []

    def clear(self) -> None:
        """Clear all buffered messages by removing the file."""
        try:
            if os.path.exists(self.buffer_file_path):
                os.unlink(self.buffer_file_path)
        except Exception:
            pass


class GuiLogHandler(logging.Handler, QObject):
    """Logging handler that routes messages to the GUI terminal area.

    This handler safely sends log messages to the GUI terminal (area A3) using
    Qt signals. It can be used from any thread and ensures proper GUI updates
    through the Qt event system.

    The handler replaces the manual add_log_message() calls throughout the
    codebase, providing a unified logging interface.
    """

    # Qt signal for thread-safe GUI updates
    log_message_signal = pyqtSignal(str)

    def __init__(self, level: int = logging.NOTSET) -> None:
        """Initialize the GUI log handler.

        :param level: Minimum log level to handle
        :type level: int
        """
        logging.Handler.__init__(self, level)
        QObject.__init__(self)
        self._main_window: Optional["MainWindow"] = None

    def set_main_window(self, main_window: "MainWindow") -> None:
        """Set the main window instance for log message routing.

        :param main_window: Main window instance with add_log_message method
        :type main_window: MainWindow
        """
        self._main_window = main_window
        # Connect signal to main window's add_log_message method
        self.log_message_signal.connect(main_window.add_log_message)

    def emit(self, record: logging.LogRecord) -> None:
        """Format and emit a log record to the GUI.

        :param record: The log record to emit
        :type record: logging.LogRecord
        """
        try:
            message = self.format(record)
            if self._main_window is not None:
                # Use signal for thread-safe GUI updates
                self.log_message_signal.emit(message)
        except Exception:
            self.handleError(record)


# Global handler instances for application-wide use
_buffer_handler: Optional[BufferHandler] = None
_gui_handler: Optional[GuiLogHandler] = None


def get_buffer_handler() -> BufferHandler:
    """Get the global buffer handler instance.

    Creates the handler if it doesn't exist yet.

    :return: The global buffer handler
    :rtype: BufferHandler
    """
    global _buffer_handler
    if _buffer_handler is None:
        _buffer_handler = BufferHandler()
        # Set a simple format for buffered messages
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        _buffer_handler.setFormatter(formatter)
    return _buffer_handler


def get_gui_handler() -> GuiLogHandler:
    """Get the global GUI handler instance.

    Creates the handler if it doesn't exist yet.

    :return: The global GUI handler
    :rtype: GuiLogHandler
    """
    global _gui_handler
    if _gui_handler is None:
        _gui_handler = GuiLogHandler()
        # Set a simple format for GUI messages
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        _gui_handler.setFormatter(formatter)
    return _gui_handler


def setup_pre_fork_logging() -> None:
    """Setup logging for the pre-fork phase.

    Adds the buffer handler to the root logger alongside any existing handlers.
    This ensures that log messages are both displayed in the terminal (if running
    from terminal) and captured for later display in the GUI.
    """
    buffer_handler = get_buffer_handler()
    root_logger = logging.getLogger()

    # Add buffer handler alongside existing handlers
    if buffer_handler not in root_logger.handlers:
        root_logger.addHandler(buffer_handler)


def setup_post_fork_logging(main_window: "MainWindow") -> None:
    """Setup logging for the post-fork GUI phase.

    1. Configures the GUI handler with the main window
    2. Adds the GUI handler to capture future log messages
    3. Replays buffered pre-fork messages through the GUI handler

    :param main_window: Main window instance
    :type main_window: MainWindow
    """
    gui_handler = get_gui_handler()
    buffer_handler = get_buffer_handler()

    # Configure GUI handler with main window
    gui_handler.set_main_window(main_window)

    # Add GUI handler to root logger FIRST so it can capture replayed messages
    root_logger = logging.getLogger()
    if gui_handler not in root_logger.handlers:
        root_logger.addHandler(gui_handler)

    # Replay buffered pre-fork messages through the GUI handler
    buffered_messages = buffer_handler.get_messages()
    for message in buffered_messages:
        # Create a log record and emit it through the GUI handler
        record = logging.LogRecord(
            name="buffered",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=message,
            args=(),
            exc_info=None,
        )
        gui_handler.emit(record)

    # Clean up the buffer file after replaying messages
    buffer_handler.clear()
