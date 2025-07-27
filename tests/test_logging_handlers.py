"""Tests for logging_handlers module."""

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock.plugin import MockerFixture

from new_python_github_project import logging_handlers
from new_python_github_project.logging_handlers import (
    BufferHandler,
    GuiLogHandler,
    get_buffer_handler,
    get_gui_handler,
    setup_post_fork_logging,
    setup_pre_fork_logging,
)


class TestGetBufferHandler:
    """Test get_buffer_handler function."""

    def test_creates_new_handler_when_none_exists(self, mocker: MockerFixture) -> None:
        """Test that get_buffer_handler creates a new handler when none exists."""
        # Reset the global handler
        mocker.patch.object(logging_handlers, "_buffer_handler", None)

        handler = get_buffer_handler()

        assert isinstance(handler, BufferHandler)
        assert handler.formatter is not None
        assert "%(levelname)s: %(message)s" in str(handler.formatter._fmt)

    def test_returns_existing_handler_when_already_created(
        self, mocker: MockerFixture
    ) -> None:
        """Test that get_buffer_handler returns existing handler when already created."""
        # Create a mock handler
        mock_handler = MagicMock(spec=BufferHandler)
        mocker.patch.object(logging_handlers, "_buffer_handler", mock_handler)

        handler = get_buffer_handler()

        assert handler is mock_handler

    def test_sets_formatter_on_new_handler(self, mocker: MockerFixture) -> None:
        """Test that get_buffer_handler sets a formatter on new handlers."""
        # Reset the global handler
        mocker.patch.object(logging_handlers, "_buffer_handler", None)

        handler = get_buffer_handler()

        assert handler.formatter is not None
        # Check that the formatter has the expected format
        test_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        formatted = handler.format(test_record)
        assert "INFO: test message" == formatted


class TestGetGuiHandler:
    """Test get_gui_handler function."""

    def test_creates_new_handler_when_none_exists(self, mocker: MockerFixture) -> None:
        """Test that get_gui_handler creates a new handler when none exists."""
        # Reset the global handler
        mocker.patch.object(logging_handlers, "_gui_handler", None)

        handler = get_gui_handler()

        assert isinstance(handler, GuiLogHandler)
        assert handler.formatter is not None
        assert "%(levelname)s: %(message)s" in str(handler.formatter._fmt)

    def test_returns_existing_handler_when_already_created(
        self, mocker: MockerFixture
    ) -> None:
        """Test that get_gui_handler returns existing handler when already created."""
        # Create a mock handler
        mock_handler = MagicMock(spec=GuiLogHandler)
        mocker.patch.object(logging_handlers, "_gui_handler", mock_handler)

        handler = get_gui_handler()

        assert handler is mock_handler

    def test_sets_formatter_on_new_handler(self, mocker: MockerFixture) -> None:
        """Test that get_gui_handler sets a formatter on new handlers."""
        # Reset the global handler
        mocker.patch.object(logging_handlers, "_gui_handler", None)

        handler = get_gui_handler()

        assert handler.formatter is not None
        # Check that the formatter has the expected format
        test_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )
        formatted = handler.format(test_record)
        assert "INFO: test message" == formatted


class TestSetupPreForkLogging:
    """Test setup_pre_fork_logging function."""

    def test_adds_buffer_handler_to_root_logger(self, mocker: MockerFixture) -> None:
        """Test that setup_pre_fork_logging adds buffer handler to root logger."""
        mock_buffer_handler = MagicMock(spec=BufferHandler)
        mock_get_buffer_handler = mocker.patch(
            "new_python_github_project.logging_handlers.get_buffer_handler",
            return_value=mock_buffer_handler,
        )
        mock_root_logger = MagicMock()
        mock_root_logger.handlers = []
        mock_get_logger = mocker.patch(
            "logging.getLogger", return_value=mock_root_logger
        )

        setup_pre_fork_logging()

        mock_get_buffer_handler.assert_called_once()
        mock_get_logger.assert_called_once_with()
        mock_root_logger.addHandler.assert_called_once_with(mock_buffer_handler)

    def test_does_not_add_handler_if_already_present(
        self, mocker: MockerFixture
    ) -> None:
        """Test that setup_pre_fork_logging doesn't add handler if already present."""
        mock_buffer_handler = MagicMock(spec=BufferHandler)
        mock_get_buffer_handler = mocker.patch(
            "new_python_github_project.logging_handlers.get_buffer_handler",
            return_value=mock_buffer_handler,
        )
        mock_root_logger = MagicMock()
        mock_root_logger.handlers = [mock_buffer_handler]
        mock_get_logger = mocker.patch(
            "logging.getLogger", return_value=mock_root_logger
        )

        setup_pre_fork_logging()

        mock_get_buffer_handler.assert_called_once()
        mock_get_logger.assert_called_once_with()
        mock_root_logger.addHandler.assert_not_called()


class TestSetupPostForkLogging:
    """Test setup_post_fork_logging function."""

    def test_configures_gui_handler_and_replays_messages(
        self, mocker: MockerFixture
    ) -> None:
        """Test that setup_post_fork_logging configures GUI handler and replays messages."""
        # Mock handlers
        mock_gui_handler = MagicMock(spec=GuiLogHandler)
        mock_buffer_handler = MagicMock(spec=BufferHandler)
        mock_buffer_handler.get_messages.return_value = [
            "INFO: test message 1",
            "ERROR: test message 2",
        ]

        # Mock getter functions
        mock_get_gui_handler = mocker.patch(
            "new_python_github_project.logging_handlers.get_gui_handler",
            return_value=mock_gui_handler,
        )
        mock_get_buffer_handler = mocker.patch(
            "new_python_github_project.logging_handlers.get_buffer_handler",
            return_value=mock_buffer_handler,
        )

        # Mock root logger
        mock_root_logger = MagicMock()
        mock_root_logger.handlers = []
        mock_get_logger = mocker.patch(
            "logging.getLogger", return_value=mock_root_logger
        )

        # Mock main window
        mock_main_window = MagicMock()

        setup_post_fork_logging(mock_main_window)

        # Verify handler configuration
        mock_get_gui_handler.assert_called_once()
        mock_get_buffer_handler.assert_called_once()
        mock_gui_handler.set_main_window.assert_called_once_with(mock_main_window)

        # Verify root logger setup
        mock_get_logger.assert_called_once_with()
        mock_root_logger.addHandler.assert_called_once_with(mock_gui_handler)

        # Verify message replay
        mock_buffer_handler.get_messages.assert_called_once()
        assert mock_gui_handler.emit.call_count == 2  # Two messages replayed

        # Verify buffer cleanup
        mock_buffer_handler.clear.assert_called_once()

    def test_does_not_add_gui_handler_if_already_present(
        self, mocker: MockerFixture
    ) -> None:
        """Test that setup_post_fork_logging doesn't add GUI handler if already present."""
        # Mock handlers
        mock_gui_handler = MagicMock(spec=GuiLogHandler)
        mock_buffer_handler = MagicMock(spec=BufferHandler)
        mock_buffer_handler.get_messages.return_value = []

        # Mock getter functions
        mocker.patch(
            "new_python_github_project.logging_handlers.get_gui_handler",
            return_value=mock_gui_handler,
        )
        mocker.patch(
            "new_python_github_project.logging_handlers.get_buffer_handler",
            return_value=mock_buffer_handler,
        )

        # Mock root logger with handler already present
        mock_root_logger = MagicMock()
        mock_root_logger.handlers = [mock_gui_handler]
        mocker.patch("logging.getLogger", return_value=mock_root_logger)

        # Mock main window
        mock_main_window = MagicMock()

        setup_post_fork_logging(mock_main_window)

        # Verify handler is not added again
        mock_root_logger.addHandler.assert_not_called()

    def test_creates_correct_log_record_for_replay(self, mocker: MockerFixture) -> None:
        """Test that setup_post_fork_logging creates correct log records for replay."""
        # Mock handlers
        mock_gui_handler = MagicMock(spec=GuiLogHandler)
        mock_buffer_handler = MagicMock(spec=BufferHandler)
        mock_buffer_handler.get_messages.return_value = ["TEST: sample message"]

        # Mock getter functions
        mocker.patch(
            "new_python_github_project.logging_handlers.get_gui_handler",
            return_value=mock_gui_handler,
        )
        mocker.patch(
            "new_python_github_project.logging_handlers.get_buffer_handler",
            return_value=mock_buffer_handler,
        )

        # Mock root logger
        mock_root_logger = MagicMock()
        mock_root_logger.handlers = []
        mocker.patch("logging.getLogger", return_value=mock_root_logger)

        # Mock main window
        mock_main_window = MagicMock()

        setup_post_fork_logging(mock_main_window)

        # Verify emit was called with a LogRecord
        mock_gui_handler.emit.assert_called_once()
        call_args = mock_gui_handler.emit.call_args[0]
        log_record = call_args[0]

        assert isinstance(log_record, logging.LogRecord)
        assert log_record.name == "buffered"
        assert log_record.levelno == logging.INFO
        assert log_record.msg == "TEST: sample message"
        assert log_record.pathname == ""
        assert log_record.lineno == 0
        assert log_record.args == ()
        assert log_record.exc_info is None


class TestBufferHandler:
    """Test BufferHandler class."""

    @pytest.fixture
    def temp_buffer_file(self, tmp_path: Path) -> Path:
        """Create a temporary buffer file for testing."""
        buffer_file = tmp_path / "test_buffer.log"
        return buffer_file

    def test_init_creates_new_temp_file_when_no_env_var(
        self, mocker: MockerFixture
    ) -> None:
        """Test BufferHandler initialization creates new temp file when no env var."""
        # Mock environment to not have existing buffer file
        mocker.patch.dict(os.environ, {}, clear=True)
        mock_tempfile = mocker.patch("tempfile.NamedTemporaryFile")
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_buffer.log"
        mock_tempfile.return_value = mock_file

        handler = BufferHandler()

        assert handler.buffer_file_path == "/tmp/test_buffer.log"
        mock_tempfile.assert_called_once_with(mode="w+", delete=False, suffix=".log")
        mock_file.close.assert_called_once()
        assert os.environ["LOGGING_BUFFER_FILE"] == "/tmp/test_buffer.log"

    def test_init_uses_existing_env_var_when_file_exists(
        self, temp_buffer_file: Path
    ) -> None:
        """Test BufferHandler initialization uses existing env var when file exists."""
        # Create the buffer file
        temp_buffer_file.write_text("existing content")

        with patch.dict(os.environ, {"LOGGING_BUFFER_FILE": str(temp_buffer_file)}):
            handler = BufferHandler()

        assert handler.buffer_file_path == str(temp_buffer_file)

    def test_emit_writes_formatted_message_to_file(
        self, temp_buffer_file: Path
    ) -> None:
        """Test that emit writes formatted message to buffer file."""
        # Create the file first
        temp_buffer_file.touch()

        with patch.dict(os.environ, {"LOGGING_BUFFER_FILE": str(temp_buffer_file)}):
            handler = BufferHandler()
            handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="test message",
                args=(),
                exc_info=None,
            )

            handler.emit(record)

            content = temp_buffer_file.read_text()
            assert "INFO: test message\n" == content

    def test_emit_handles_exception_gracefully(self, mocker: MockerFixture) -> None:
        """Test that emit handles exceptions by calling handleError."""
        handler = BufferHandler()
        handler.buffer_file_path = "/nonexistent/path/file.log"
        mock_handle_error = mocker.patch.object(handler, "handleError")

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        mock_handle_error.assert_called_once_with(record)

    def test_get_messages_reads_from_existing_file(
        self, temp_buffer_file: Path
    ) -> None:
        """Test that get_messages reads messages from existing file."""
        temp_buffer_file.write_text("line1\nline2\nline3\n")

        with patch.dict(os.environ, {"LOGGING_BUFFER_FILE": str(temp_buffer_file)}):
            handler = BufferHandler()

            messages = handler.get_messages()

            assert ["line1", "line2", "line3"] == messages

    def test_get_messages_returns_empty_list_when_file_not_exists(
        self, mocker: MockerFixture
    ) -> None:
        """Test that get_messages returns empty list when file doesn't exist."""
        handler = BufferHandler()
        handler.buffer_file_path = "/nonexistent/file.log"

        messages = handler.get_messages()

        assert [] == messages

    def test_get_messages_handles_exception_gracefully(
        self, mocker: MockerFixture
    ) -> None:
        """Test that get_messages handles exceptions by returning empty list."""
        handler = BufferHandler()
        handler.buffer_file_path = "/nonexistent/path/file.log"

        # Mock Path.exists to return True but open to fail
        mock_path = mocker.patch("pathlib.Path")
        mock_path.return_value.exists.return_value = True
        mocker.patch("builtins.open", side_effect=PermissionError("Access denied"))

        messages = handler.get_messages()

        assert [] == messages

    def test_clear_removes_existing_file(self, temp_buffer_file: Path) -> None:
        """Test that clear removes the buffer file."""
        temp_buffer_file.write_text("some content")

        with patch.dict(os.environ, {"LOGGING_BUFFER_FILE": str(temp_buffer_file)}):
            handler = BufferHandler()

            handler.clear()

            assert not temp_buffer_file.exists()

    def test_clear_handles_exception_gracefully(self, mocker: MockerFixture) -> None:
        """Test that clear handles exceptions gracefully."""
        handler = BufferHandler()
        handler.buffer_file_path = "/nonexistent/file.log"

        # Mock Path.exists to return True but unlink to fail
        mock_path = mocker.patch("pathlib.Path")
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.unlink.side_effect = PermissionError("Access denied")

        # Should not raise exception
        handler.clear()


class TestGuiLogHandler:
    """Test GuiLogHandler class."""

    @pytest.fixture
    def mock_main_window(self) -> MagicMock:
        """Create a mock main window for testing."""
        mock_window = MagicMock()
        mock_window.add_log_message = MagicMock()
        return mock_window

    def test_init_sets_main_window_to_none(self) -> None:
        """Test that GuiLogHandler initialization sets main window to None."""
        handler = GuiLogHandler()

        assert handler._main_window is None

    def test_set_main_window_configures_handler(
        self, mock_main_window: MagicMock
    ) -> None:
        """Test that set_main_window configures the handler correctly."""
        handler = GuiLogHandler()

        handler.set_main_window(mock_main_window)

        assert handler._main_window is mock_main_window
        # Verify signal connection (signal should be connected but we can't easily test it)

    def test_emit_sends_message_when_main_window_set(
        self, mock_main_window: MagicMock
    ) -> None:
        """Test that emit sends message to GUI when main window is set."""
        handler = GuiLogHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        handler.set_main_window(mock_main_window)

        # Capture emitted signals
        emitted_messages = []
        handler.log_message_signal.connect(lambda msg: emitted_messages.append(msg))

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        assert ["INFO: test message"] == emitted_messages

    def test_emit_does_nothing_when_main_window_not_set(self) -> None:
        """Test that emit does nothing when main window is not set."""
        handler = GuiLogHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        # Capture emitted signals
        emitted_messages = []
        handler.log_message_signal.connect(lambda msg: emitted_messages.append(msg))

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # No messages should be emitted since main window is not set
        assert [] == emitted_messages

    def test_emit_handles_exception_gracefully(
        self, mock_main_window: MagicMock, mocker: MockerFixture
    ) -> None:
        """Test that emit handles exceptions by calling handleError."""
        handler = GuiLogHandler()
        handler.set_main_window(mock_main_window)
        mock_handle_error = mocker.patch.object(handler, "handleError")

        # Mock format to raise an exception
        mocker.patch.object(handler, "format", side_effect=Exception("Format error"))

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        mock_handle_error.assert_called_once_with(record)
