import logging
from typing import cast, List, Optional

from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QTextEdit,
    QMainWindow,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QFont,
    QTextCursor,
    QAction,
    QGuiApplication,
    QResizeEvent,
    QCloseEvent,
    QIcon,
)
from PyQt6.QtWidgets import QApplication

from new_python_github_project.config import Config
from new_python_github_project.task import Task, TaskItemWidget
from new_python_github_project import logging_handlers


class TaskListFrame(QFrame):
    """Frame containing the task list with scrollable area.

    This class provides a scrollable list of tasks that users need to complete
    before creating a new Python project. Tasks are organized in logical sections
    and some have default values while others require user input.

    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional

    .. versionadded:: 1.0.0
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the TaskListFrame.

        Sets up the UI and loads sample tasks for the project creation workflow.

        :param parent: Parent widget
        :type parent: QWidget, optional
        """
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_tasks()

    def setup_ui(self) -> None:
        """Setup the task list frame UI components.

        Creates the main layout, title label, scroll area, and container widget
        for the task items. Configures scrolling behavior and frame styling.
        """
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Title
        title = QLabel("Tasks")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Scroll area for tasks
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Container widget for tasks
        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setSpacing(5)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.tasks_widget)
        layout.addWidget(self.scroll_area)

        # Style the frame
        self.setFrameStyle(QFrame.Shape.Box)

    def load_sample_tasks(self) -> None:
        """Load sample tasks for the project creation workflow.

        Creates and loads tasks organized in logical sections that follow the natural
        progression of setting up a Python project. Tasks are ordered to minimize
        cognitive load and follow dependencies.

        **Task Ordering Logic:**

        1. **Project Fundamentals**: Name, directory location
        2. **Technical Foundation**: Python version, license
        3. **Project Metadata**: Description, author information
        4. **Development Tools**: Testing framework, code style
        5. **Deployment & Repository**: Repository URL

        **When Adding New Tasks:**

        - Consider where the task fits in the logical workflow
        - Place it in the appropriate section
        - Update section comments if needed
        - Ensure the task description is unique

        .. note::
           Tasks with ``has_default=False`` require user input before project creation
           can proceed. Tasks with defaults can use their default values.
        """
        import os

        # Get current directory as default for project directory
        current_dir = os.getcwd()

        # ============================================================================
        # SECTION 1: PROJECT FUNDAMENTALS (Name, Location)
        # These are the basic identity and location of the project
        # ============================================================================
        project_fundamentals = [
            Task(
                "Set project name", has_default=False
            ),  # Required - no sensible default
            Task(
                "Set project directory", has_default=True, default_value=current_dir
            ),  # Default to current directory
        ]

        # ============================================================================
        # SECTION 2: TECHNICAL FOUNDATION (Language, License)
        # These define the technical environment and legal framework
        # ============================================================================
        technical_foundation = [
            Task(
                "Choose Python version", has_default=True, default_value=">=3.8"
            ),  # Default to Python 3.8+
            Task(
                "Choose license", has_default=True, default_value="MIT"
            ),  # Default to MIT
        ]

        # ============================================================================
        # SECTION 3: PROJECT METADATA (Description, Author)
        # These provide context and attribution for the project
        # ============================================================================
        project_metadata = [
            Task(
                "Set project description", has_default=False
            ),  # Required - no sensible default
            Task(
                "Set author name", has_default=True, default_value="Håkon Hægland"
            ),  # Default from config file
        ]

        # ============================================================================
        # SECTION 4: DEVELOPMENT TOOLS (Testing, Code Style)
        # These configure the development environment and quality tools
        # ============================================================================
        development_tools = [
            Task("Choose testing framework", has_default=True),  # Has sensible default
            Task(
                "Set package name", has_default=False
            ),  # Required - depends on project name
            Task("Choose code style", has_default=True),  # Has sensible default
        ]

        # ============================================================================
        # SECTION 5: DEPLOYMENT & REPOSITORY (Repository URL)
        # These are for publishing and sharing the project
        # ============================================================================
        deployment_repository = [
            Task("Set repository URL", has_default=False),  # Optional but common
        ]

        # Combine all sections in logical order
        sample_tasks = (
            project_fundamentals
            + technical_foundation
            + project_metadata
            + development_tools
            + deployment_repository
        )

        for task in sample_tasks:
            task_widget = TaskItemWidget(task)
            self.tasks_layout.addWidget(task_widget)

        # Store reference to all tasks for validation
        self.all_tasks = sample_tasks

    def get_incomplete_required_tasks(self) -> List[Task]:
        """Get list of tasks that require user input but are not completed.

        Iterates through all tasks to find those that have no default value
        and are not yet completed by the user. These tasks must be completed
        before project creation can proceed.

        :returns: List of Task objects that have no default and are not completed
        :rtype: list[Task]

        .. seealso::
           :class:`~new_python_github_project.task.Task` for task structure
        """
        incomplete_tasks = []
        for task in self.all_tasks:
            # Check if task requires user input (no default) and is not completed
            if not task.has_default and not task.is_completed:
                incomplete_tasks.append(task)
        return incomplete_tasks


class ActionButtonsFrame(QFrame):
    """Frame containing action buttons for project operations.

    This frame provides the main action buttons for the application,
    primarily the "Create" button that initiates project creation after
    validating that all required tasks are completed.

    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional

    .. versionadded:: 1.0.0
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the ActionButtonsFrame.

        Sets up the UI with action buttons.

        :param parent: Parent widget
        :type parent: QWidget, optional
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the action buttons frame UI components.

        Creates the layout, title label, and action buttons. Currently includes
        a "Create" button with styling and click handler. The button is positioned
        to the left with proper spacing and visual styling.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Title
        title = QLabel("Actions")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Create button
        create_button = QPushButton("Create")
        create_button.setMinimumHeight(30)
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        create_button.clicked.connect(self.on_create_clicked)

        button_layout.addWidget(create_button)
        button_layout.addStretch()  # Push button to the left

        layout.addLayout(button_layout)

        # Style the frame
        self.setFrameStyle(QFrame.Shape.Box)

    def on_create_clicked(self) -> None:
        """Handle create button click event.

        Validates that all required tasks are completed before proceeding with
        project creation. If incomplete tasks exist, shows an error dialog.
        Otherwise, proceeds with project creation and logs progress messages.

        .. note::
           This method accesses the parent MainWindow to get the task list
           and add log messages.
        """
        # Get the main window and cast it to MainWindow type
        main_window = cast("MainWindow", self.window())

        # Get the task list frame to access tasks
        task_list_frame = main_window.task_list

        # Check for incomplete required tasks
        incomplete_tasks = task_list_frame.get_incomplete_required_tasks()

        if incomplete_tasks:
            # Show error dialog with list of incomplete tasks
            self.show_incomplete_tasks_dialog(incomplete_tasks)
        else:
            # All required tasks are completed, proceed with project creation
            logging.info(
                "✓ All tasks completed! Project structure creation would proceed here."
            )
            logging.info("📁 Creating project structure...")
            logging.info("📄 Generating configuration files...")
            logging.info("✅ Project setup complete!")

    def show_incomplete_tasks_dialog(self, incomplete_tasks: List[Task]) -> None:
        """Show error dialog listing incomplete required tasks.

        Displays a critical message box with a list of tasks that require
        user input before project creation can proceed.

        :param incomplete_tasks: List of tasks that need to be completed
        :type incomplete_tasks: list[Task]

        .. seealso::
           :meth:`get_incomplete_required_tasks` for task validation logic
        """
        # Build the message
        message = (
            "The following tasks require your input before creating the project:\n\n"
        )

        for task in incomplete_tasks:
            message += f"• {task.description}\n"

        message += "\nPlease complete these tasks and try again."

        # Show error dialog
        QMessageBox.critical(
            self, "Incomplete Tasks", message, QMessageBox.StandardButton.Ok
        )


class TerminalFrame(QFrame):
    """Frame containing the terminal-like output area.

    This frame provides a read-only terminal-like interface for displaying
    log messages and application output. Messages are timestamped and
    automatically scrolled to keep the latest output visible.

    :param parent: Parent widget, defaults to None
    :type parent: QWidget, optional

    .. versionadded:: 1.0.0
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """Initialize the TerminalFrame.

        Sets up the UI and loads sample output messages.

        :param parent: Parent widget
        :type parent: QWidget, optional
        """
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_output()

    def setup_ui(self) -> None:
        """Setup the terminal frame UI components.

        Creates the layout, title label, and terminal text area. The terminal
        uses a monospace font with dark theme styling and is configured as
        read-only with word wrapping enabled.
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Title
        title = QLabel("Terminal Output")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 10px;")
        layout.addWidget(title)

        # Terminal text area
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Monospace", 10))
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
            }
        """)

        # Set line wrap mode to wrap at word boundaries
        self.terminal.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        layout.addWidget(self.terminal)

        # Style the frame
        self.setFrameStyle(QFrame.Shape.Box)

    def load_sample_output(self) -> None:
        """Load sample terminal output messages.

        Populates the terminal with sample log messages to demonstrate
        the output format and behavior. Includes messages of varying
        lengths to test text wrapping.
        """
        sample_messages = [
            "Application started successfully",
            "Loading configuration...",
            "Configuration loaded successfully",
            "Initializing UI components...",
            "UI components initialized",
            "Ready for user interaction",
            "This is a very long log message that demonstrates how the terminal handles long lines that need to be wrapped at the right edge of the window without horizontal scrollbars",
            "Another message with reasonable length",
            "System status: OK",
            "All services running normally",
        ]

        for message in sample_messages:
            logging.info(message)

    def add_log_message(self, message: str) -> None:
        """Add a log message to the terminal output.

        Appends a timestamped message to the terminal and automatically
        scrolls to keep the new message visible. The timestamp format
        is HH:MM:SS.

        :param message: The message to add to the terminal
        :type message: str

        .. note::
           Messages are automatically timestamped with the current time
           when they are added to the terminal.
        """
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.terminal.setTextCursor(cursor)

        # Add timestamp and message
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        self.terminal.insertPlainText(formatted_message)

        # Auto-scroll to bottom
        self.terminal.ensureCursorVisible()


class MainWindow(QMainWindow):
    """Main application window with three vertical areas.

    The main window implements a three-area layout design:

    - **Area A1 (42.5%)**: Task list showing project configuration tasks
    - **Area A2 (10%)**: Action buttons for project operations
    - **Area A3 (42.5%)**: Terminal output for logging and feedback

    The window automatically adjusts its size to fit the available screen space
    and centers itself on the screen. It includes a menu bar with basic file
    operations and provides logging capabilities for user feedback.

    :param app: The QApplication instance
    :type app: QApplication
    :param config: Application configuration object
    :type config: Config

    .. versionadded:: 1.0.0
    """

    def __init__(self, app: QApplication, config: Config):
        """Initialize the MainWindow.

        :param app: The QApplication instance
        :type app: QApplication
        :param config: Application configuration object
        :type config: Config
        """
        super().__init__()
        self.app = app
        self.config = config
        self._setup_ui()

        # Setup post-fork logging to replay buffered messages and route future logs to GUI
        logging_handlers.setup_post_fork_logging(self)

    # -----------------
    # Public methods
    # -----------------

    def add_log_message(self, message: str) -> None:
        """Add a log message to the terminal output.

        Convenience method that forwards log messages to the terminal frame.
        This allows other components to easily add messages to the terminal
        through the main window.

        :param message: The message to add to the terminal
        :type message: str

        .. seealso::
           :meth:`TerminalFrame.add_log_message` for the actual implementation
        """
        self.terminal_frame.add_log_message(message)

    def closeEvent(self, event: Optional[QCloseEvent]) -> None:
        """Handle window close events.

        When the user closes the window with the X button, this ensures
        the application properly quits so the lockfile is cleaned up.

        :param event: The close event
        :type event: QCloseEvent
        """
        logging.info("Window close requested")
        if event is not None:
            event.accept()
        self.app.quit()

    def resizeEvent(self, event: Optional[QResizeEvent]) -> None:
        """Handle window resize events.

        Logs the new window dimensions to the terminal when the user
        resizes the window. This provides feedback about the current
        window state.

        :param event: The resize event containing new dimensions
        :type event: QResizeEvent

        .. note::
           This method overrides the base class resize event handler
           and calls the parent implementation before logging.
        """
        super().resizeEvent(event)
        if event is not None:
            width = event.size().width()
            height = event.size().height()
            logging.info(f"Window resized to: {width}x{height} pixels")

    # -----------------
    # Private methods
    # -----------------

    def _configure_window_size_and_position(self) -> tuple[int, int]:
        """Configure window size and position based on screen dimensions.

        Reads default window size from config, detects screen size, adjusts
        window size if needed to fit screen with margin, and centers the window.

        :returns: Tuple of (default_width, default_height) from config
        :rtype: tuple[int, int]
        """
        # Set default window size
        default_width = self.config.getint("MainWindow", "width")
        default_height = self.config.getint("MainWindow", "height")

        # Get screen size and adjust window size if needed
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            screen_geometry = screen.availableGeometry()
            self.screen_width = screen_geometry.width()
            self.screen_height = screen_geometry.height()
        else:
            # Fallback to default screen size if primary screen is not available
            self.screen_width = 1920
            self.screen_height = 1080

        # Adjust window size if it's too large for the screen
        # Leave some margin (50 pixels) to ensure window fits
        max_width = self.screen_width - 50
        max_height = self.screen_height - 50

        self.window_width = min(default_width, max_width)
        self.window_height = min(default_height, max_height)

        # Center the window on screen
        x = (self.screen_width - self.window_width) // 2
        y = (self.screen_height - self.window_height) // 2

        self.setGeometry(x, y, self.window_width, self.window_height)

        return default_width, default_height

    def _create_ui_components(self, layout: QVBoxLayout) -> None:
        """Create and add the main UI components to the layout.

        Creates the three main areas: task list, action buttons, and terminal output.
        Sets up the terminal reference for other components to use.

        :param layout: The main vertical layout to add components to
        :type layout: QVBoxLayout
        """
        # Area A1: Task List (42.5% of height)
        self.task_list = TaskListFrame()
        layout.addWidget(self.task_list, 42)

        # Area A2: Action Buttons (10% of height)
        self.action_buttons = ActionButtonsFrame()
        layout.addWidget(self.action_buttons, 10)

        # Area A3: Terminal Output (42.5% of height)
        self.terminal_frame = TerminalFrame()
        layout.addWidget(self.terminal_frame, 42)

        # Store reference to terminal for other components
        self.terminal = self.terminal_frame.terminal

    def _log_window_size_info(self) -> None:
        """Log window size information for debugging and user feedback.

        Logs the detected screen size, final window size, and whether
        the window size was adjusted to fit the screen.
        """
        # Get the original default sizes for comparison
        default_width = self.config.getint("MainWindow", "width")
        default_height = self.config.getint("MainWindow", "height")

        logging.info(f"Screen size: {self.screen_width}x{self.screen_height}")
        logging.info(f"Window size: {self.window_width}x{self.window_height}")
        if self.window_width < default_width or self.window_height < default_height:
            logging.info("Window size adjusted to fit screen")

    def _set_window_icon(self) -> None:
        """Set the window icon explicitly for better cross-platform compatibility.

        This method sets the window icon directly on the MainWindow, which is
        especially important on Windows where the application-level icon may not
        always be properly displayed in the taskbar and window title bar.

        Since _load_icons() has already set the application icon via app.setWindowIcon(),
        we can retrieve and reuse that same icon for consistency across all platforms.
        """
        # Try to use the application icon that was already loaded
        app_icon = self.app.windowIcon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)
            logging.info("Window icon set from application icon")
        else:
            # Fallback to theme icon if application icon is not available
            fallback_icon = QIcon.fromTheme("applications-python")
            self.setWindowIcon(fallback_icon)
            logging.info("Window icon set to fallback theme icon")

    def _setup_layout(self) -> QVBoxLayout:
        """Setup the central widget and main layout.

        Creates the central widget, sets it on the main window, and creates
        the main vertical layout with appropriate margins and spacing.

        :returns: The main vertical layout for adding components
        :rtype: QVBoxLayout
        """
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        return layout

    def _setup_menu(self) -> None:
        """Setup the menu bar with file operations.

        Creates a File menu with a Quit action (Ctrl+Q shortcut).
        The menu provides standard application controls and keyboard shortcuts.
        """
        menubar = self.menuBar()
        if menubar is not None:
            # File menu
            file_menu = menubar.addMenu("File")
            if file_menu is not None:
                # Quit action
                quit_action = QAction("Quit", self)
                quit_action.setShortcut("Ctrl+Q")
                quit_action.setStatusTip("Quit the application")
                quit_action.triggered.connect(self.close)
                file_menu.addAction(quit_action)

    def _setup_ui(self) -> None:
        """Setup the main window UI components.

        Creates the main window layout with three vertical areas, configures
        window sizing based on screen dimensions, centers the window, and
        initializes all UI components including menu bar, task list, action
        buttons, and terminal output.

        The window size is automatically adjusted if the default size exceeds
        the available screen space, with a 50-pixel margin maintained.
        """
        # Basic window properties
        self.setWindowTitle("Python Project Creator")
        self.setObjectName("QMainWindow")
        self._set_window_icon()

        # Configure window size and position
        self._configure_window_size_and_position()

        # Setup menu bar
        self._setup_menu()

        # Setup layout and UI components
        layout = self._setup_layout()
        self._create_ui_components(layout)

        # Log the window size information
        self._log_window_size_info()
