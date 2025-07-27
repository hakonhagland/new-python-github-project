"""Unit tests for main_window.py."""

import re

from PyQt6.QtWidgets import QApplication, QMessageBox, QPushButton
from pytest_mock.plugin import MockerFixture
from pytestqt.qtbot import QtBot

from new_python_github_project.main_window import (
    ActionButtonsFrame,
    MainWindow,
    TaskListFrame,
    TerminalFrame,
)

from .common import GetConfig


class TestMainWindow:
    """Test cases for MainWindow class."""

    def test_constructor(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test MainWindow constructor initializes correctly.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock the setup_post_fork_logging to avoid side effects
        mock_setup_logging = mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )

        # Mock the _setup_ui method to isolate constructor testing
        mock_setup_ui = mocker.patch.object(MainWindow, "_setup_ui")

        # Get test configuration
        config = get_config()

        # Get QApplication instance (provided by qtbot)
        app = QApplication.instance()
        assert app is not None, "QApplication should exist"
        assert isinstance(app, QApplication), "Should be QApplication instance"

        # Create MainWindow instance
        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Verify constructor set instance variables correctly
        assert window.app is app
        assert window.config is config

        # Verify setup methods were called
        mock_setup_ui.assert_called_once()
        mock_setup_logging.assert_called_once_with(window)

    def test_setup_ui(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test MainWindow setup_ui method creates UI components correctly.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock logging to avoid side effects during UI setup
        mocker.patch("new_python_github_project.main_window.logging")

        # Mock the _set_window_icon method to avoid icon-related side effects
        mock_set_icon = mocker.patch.object(MainWindow, "_set_window_icon")

        # Mock the _setup_menu method to isolate UI layout testing
        mock_setup_menu = mocker.patch.object(MainWindow, "_setup_menu")

        # Mock QGuiApplication.primaryScreen() to control screen size
        mock_screen = mocker.MagicMock()
        mock_screen.availableGeometry.return_value.width.return_value = 1920
        mock_screen.availableGeometry.return_value.height.return_value = 1080
        mocker.patch(
            "new_python_github_project.main_window.QGuiApplication.primaryScreen",
            return_value=mock_screen,
        )

        # Get test configuration and app
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        # Create MainWindow instance with mocked setup_post_fork_logging
        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Verify window properties were set correctly
        assert window.windowTitle() == "Python Project Creator"
        assert window.objectName() == "QMainWindow"

        # Verify screen size and window size attributes were set
        assert hasattr(window, "screen_width")
        assert hasattr(window, "screen_height")
        assert hasattr(window, "window_width")
        assert hasattr(window, "window_height")
        assert window.screen_width == 1920
        assert window.screen_height == 1080

        # Verify UI components were created
        assert hasattr(window, "task_list")
        assert hasattr(window, "action_buttons")
        assert hasattr(window, "terminal_frame")
        assert hasattr(window, "terminal")

        # Verify setup methods were called
        mock_set_icon.assert_called_once()
        mock_setup_menu.assert_called_once()

        # Verify central widget was set
        assert window.centralWidget() is not None

    def test_configure_window_size_and_position_no_screen(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test _configure_window_size_and_position with no primary screen available.

        This test covers the fallback case when QGuiApplication.primaryScreen()
        returns None, ensuring the method uses default screen dimensions.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock QGuiApplication.primaryScreen() to return None (no screen available)
        mocker.patch(
            "new_python_github_project.main_window.QGuiApplication.primaryScreen",
            return_value=None,
        )

        # Get test configuration and app
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        # Mock other methods to isolate _configure_window_size_and_position
        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        mocker.patch.object(MainWindow, "_set_window_icon")
        mocker.patch.object(MainWindow, "_setup_menu")
        mocker.patch.object(
            MainWindow, "_setup_layout", return_value=mocker.MagicMock()
        )
        mocker.patch.object(MainWindow, "_create_ui_components")
        mocker.patch.object(MainWindow, "_log_window_size_info")

        # Create MainWindow instance - this will call _configure_window_size_and_position
        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Verify fallback screen dimensions were used (lines 588-589)
        assert window.screen_width == 1920
        assert window.screen_height == 1080

    def test_resize_event_with_valid_event(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test resizeEvent method with a valid QResizeEvent.

        This test verifies that resizeEvent correctly handles a valid resize event,
        calls the parent implementation, extracts dimensions, and logs the information.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock logging to capture log messages
        mock_logging = mocker.patch("new_python_github_project.main_window.logging")

        # Create MainWindow instance with mocked dependencies
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        mocker.patch.object(MainWindow, "_setup_ui")

        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Create a mock QResizeEvent with specific dimensions
        mock_event = mocker.MagicMock()
        mock_size = mocker.MagicMock()
        mock_size.width.return_value = 800
        mock_size.height.return_value = 600
        mock_event.size.return_value = mock_size

        # Mock the parent resizeEvent to verify it's called
        mock_super_resize = mocker.patch("PyQt6.QtWidgets.QMainWindow.resizeEvent")

        # Call resizeEvent with the mock event
        window.resizeEvent(mock_event)

        # Verify parent resizeEvent was called with the event
        mock_super_resize.assert_called_once_with(mock_event)

        # Verify logging was called with the correct message
        mock_logging.info.assert_called_once_with("Window resized to: 800x600 pixels")

    def test_resize_event_with_none_event(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test resizeEvent method with None event.

        This test verifies that resizeEvent correctly handles a None event by
        only calling the parent implementation without attempting to log dimensions.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock logging to verify it's not called
        mock_logging = mocker.patch("new_python_github_project.main_window.logging")

        # Create MainWindow instance with mocked dependencies
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        mocker.patch.object(MainWindow, "_setup_ui")

        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Mock the parent resizeEvent to verify it's called
        mock_super_resize = mocker.patch("PyQt6.QtWidgets.QMainWindow.resizeEvent")

        # Call resizeEvent with None
        window.resizeEvent(None)

        # Verify parent resizeEvent was called with None
        mock_super_resize.assert_called_once_with(None)

        # Verify logging was NOT called (since event is None)
        mock_logging.info.assert_not_called()

    def test_add_log_message(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test add_log_message method forwards messages to terminal frame.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Create MainWindow instance with mocked dependencies
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        mocker.patch.object(MainWindow, "_setup_ui")

        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Mock the terminal_frame and its add_log_message method
        mock_terminal_frame = mocker.MagicMock()
        window.terminal_frame = mock_terminal_frame

        # Call add_log_message
        test_message = "Test log message"
        window.add_log_message(test_message)

        # Verify the message was forwarded to terminal_frame
        mock_terminal_frame.add_log_message.assert_called_once_with(test_message)

    def test_closeEvent(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test closeEvent method logs and quits application.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock logging
        mock_logging = mocker.patch("new_python_github_project.main_window.logging")

        # Create MainWindow instance with mocked dependencies
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        mocker.patch.object(MainWindow, "_setup_ui")

        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Mock app.quit to verify it's called
        mock_quit = mocker.patch.object(window.app, "quit")

        # Create a mock close event
        mock_event = mocker.MagicMock()

        # Call closeEvent
        window.closeEvent(mock_event)

        # Verify logging was called
        mock_logging.info.assert_called_once_with("Window close requested")

        # Verify event was accepted
        mock_event.accept.assert_called_once()

        # Verify app.quit was called
        mock_quit.assert_called_once()

    def test_log_window_size_info_with_adjustment(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test _log_window_size_info when window size was adjusted.

        This covers the conditional logging when window size had to be adjusted
        to fit the screen (line 644).

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock logging
        mock_logging = mocker.patch("new_python_github_project.main_window.logging")

        # Create MainWindow instance with mocked dependencies
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        mocker.patch.object(MainWindow, "_setup_ui")

        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Set up window dimensions that would trigger the adjustment message
        # Make actual window smaller than config defaults to trigger line 644
        window.screen_width = 1920
        window.screen_height = 1080
        window.window_width = 800  # Smaller than default (probably 1024)
        window.window_height = 600  # Smaller than default (probably 768)

        # Call _log_window_size_info directly
        window._log_window_size_info()

        # Verify all logging calls were made
        expected_calls = [
            mocker.call("Screen size: 1920x1080"),
            mocker.call("Window size: 800x600"),
            mocker.call("Window size adjusted to fit screen"),  # This is line 644
        ]
        mock_logging.info.assert_has_calls(expected_calls)

    def test_set_window_icon_with_app_icon(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test _set_window_icon when app icon is available.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock logging
        mock_logging = mocker.patch("new_python_github_project.main_window.logging")

        # Create MainWindow instance with mocked dependencies
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        mocker.patch.object(MainWindow, "_setup_ui")

        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Mock app icon to be valid (not null)
        mock_app_icon = mocker.MagicMock()
        mock_app_icon.isNull.return_value = False
        mocker.patch.object(window.app, "windowIcon", return_value=mock_app_icon)

        # Mock setWindowIcon to verify it's called
        mock_set_icon = mocker.patch.object(window, "setWindowIcon")

        # Call _set_window_icon
        window._set_window_icon()

        # Verify app icon was used
        mock_set_icon.assert_called_once_with(mock_app_icon)
        mock_logging.info.assert_called_once_with(
            "Window icon set from application icon"
        )

    def test_set_window_icon_fallback(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test _set_window_icon fallback when no app icon available.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock logging
        mock_logging = mocker.patch("new_python_github_project.main_window.logging")

        # Create MainWindow instance with mocked dependencies
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        mocker.patch.object(MainWindow, "_setup_ui")

        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Mock app icon to be null (not available)
        mock_app_icon = mocker.MagicMock()
        mock_app_icon.isNull.return_value = True
        mocker.patch.object(window.app, "windowIcon", return_value=mock_app_icon)

        # Mock QIcon.fromTheme and setWindowIcon
        mock_fallback_icon = mocker.MagicMock()
        mock_from_theme = mocker.patch(
            "new_python_github_project.main_window.QIcon.fromTheme",
            return_value=mock_fallback_icon,
        )
        mock_set_icon = mocker.patch.object(window, "setWindowIcon")

        # Call _set_window_icon
        window._set_window_icon()

        # Verify fallback icon was used
        mock_from_theme.assert_called_once_with("applications-python")
        mock_set_icon.assert_called_once_with(mock_fallback_icon)
        mock_logging.info.assert_called_once_with(
            "Window icon set to fallback theme icon"
        )

    def test_setup_menu(
        self, qtbot: QtBot, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test _setup_menu creates menu bar with quit action.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param get_config: Fixture to get a test Config instance
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Create MainWindow instance with mocked dependencies
        config = get_config()
        app = QApplication.instance()
        assert app is not None and isinstance(app, QApplication)

        mocker.patch(
            "new_python_github_project.main_window.logging_handlers.setup_post_fork_logging"
        )
        mocker.patch.object(MainWindow, "_setup_ui")

        window = MainWindow(app, config)
        qtbot.addWidget(window)

        # Mock menu bar and file menu
        mock_file_menu = mocker.MagicMock()
        mock_menubar = mocker.MagicMock()
        mock_menubar.addMenu.return_value = mock_file_menu
        mock_menubar_method = mocker.patch.object(
            window, "menuBar", return_value=mock_menubar
        )

        # Mock QAction creation
        mock_quit_action = mocker.MagicMock()
        mock_qaction = mocker.patch(
            "new_python_github_project.main_window.QAction",
            return_value=mock_quit_action,
        )

        # Call _setup_menu
        window._setup_menu()

        # Verify menu bar was accessed
        mock_menubar_method.assert_called_once()

        # Verify File menu was created
        mock_menubar.addMenu.assert_called_once_with("File")

        # Verify Quit action was created and configured
        mock_qaction.assert_called_once_with("Quit", window)
        mock_quit_action.setShortcut.assert_called_once_with("Ctrl+Q")
        mock_quit_action.setStatusTip.assert_called_once_with("Quit the application")
        mock_quit_action.triggered.connect.assert_called_once_with(window.close)

        # Verify action was added to file menu
        mock_file_menu.addAction.assert_called_once_with(mock_quit_action)


class TestTerminalFrame:
    """Test cases for TerminalFrame class."""

    def test_constructor(self, qtbot: QtBot, mocker: MockerFixture) -> None:
        """Test TerminalFrame constructor initializes correctly.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock the setup_ui and load_sample_output methods to isolate constructor
        mock_setup_ui = mocker.patch.object(TerminalFrame, "setup_ui")
        mock_load_sample = mocker.patch.object(TerminalFrame, "load_sample_output")

        # Create TerminalFrame instance
        terminal = TerminalFrame()
        qtbot.addWidget(terminal)

        # Verify setup methods were called
        mock_setup_ui.assert_called_once()
        mock_load_sample.assert_called_once()

    def test_setup_ui(self, qtbot: QtBot, mocker: MockerFixture) -> None:
        """Test TerminalFrame setup_ui creates UI components correctly.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock load_sample_output to isolate setup_ui testing
        mocker.patch.object(TerminalFrame, "load_sample_output")

        # Create TerminalFrame instance
        terminal = TerminalFrame()
        qtbot.addWidget(terminal)

        # Verify UI components were created
        assert hasattr(terminal, "terminal")
        assert terminal.terminal is not None

        # Verify terminal properties
        assert terminal.terminal.isReadOnly()
        assert (
            terminal.terminal.lineWrapMode()
            == terminal.terminal.LineWrapMode.WidgetWidth
        )

        # Verify frame style was set
        assert terminal.frameStyle() == terminal.Shape.Box

    def test_load_sample_output(self, qtbot: QtBot, mocker: MockerFixture) -> None:
        """Test TerminalFrame load_sample_output logs sample messages.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock logging to capture log calls
        mock_logging = mocker.patch("new_python_github_project.main_window.logging")

        # Mock setup_ui to isolate load_sample_output testing
        mocker.patch.object(TerminalFrame, "setup_ui")

        # Create TerminalFrame instance - this will call load_sample_output
        terminal = TerminalFrame()
        qtbot.addWidget(terminal)

        # Verify logging.info was called for each sample message
        assert mock_logging.info.call_count == 10  # 10 sample messages

        # Verify some specific sample messages were logged
        expected_calls = [
            mocker.call("Application started successfully"),
            mocker.call("Loading configuration..."),
            mocker.call("Configuration loaded successfully"),
            mocker.call("Ready for user interaction"),
            mocker.call("System status: OK"),
        ]
        mock_logging.info.assert_has_calls(expected_calls, any_order=True)

    def test_add_log_message(self, qtbot: QtBot, mocker: MockerFixture) -> None:
        """Test TerminalFrame add_log_message adds timestamped messages.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock load_sample_output to avoid sample messages during testing
        mocker.patch.object(TerminalFrame, "load_sample_output")

        # Create TerminalFrame instance
        terminal = TerminalFrame()
        qtbot.addWidget(terminal)

        # Mock datetime to control timestamp (it's imported inside the method)
        mock_datetime = mocker.MagicMock()
        mock_datetime.now.return_value.strftime.return_value = "12:34:56"
        mocker.patch("datetime.datetime", mock_datetime)

        # Mock the key terminal methods we want to verify
        mock_insert_text = mocker.patch.object(terminal.terminal, "insertPlainText")
        mock_ensure_visible = mocker.patch.object(
            terminal.terminal, "ensureCursorVisible"
        )

        # Call add_log_message
        test_message = "Test log message"
        terminal.add_log_message(test_message)

        # Verify formatted message was inserted with correct timestamp
        expected_formatted = "[12:34:56] Test log message\n"
        mock_insert_text.assert_called_once_with(expected_formatted)

        # Verify auto-scroll was called
        mock_ensure_visible.assert_called_once()

    def test_add_log_message_real_timestamp(
        self, qtbot: QtBot, mocker: MockerFixture
    ) -> None:
        """Test TerminalFrame add_log_message with real timestamp formatting.

        This test verifies the timestamp format without mocking datetime.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock load_sample_output to avoid sample messages during testing
        mocker.patch.object(TerminalFrame, "load_sample_output")

        # Create TerminalFrame instance
        terminal = TerminalFrame()
        qtbot.addWidget(terminal)

        # Mock only the text insertion to capture the formatted message
        mock_insert_text = mocker.patch.object(terminal.terminal, "insertPlainText")

        # Call add_log_message with real timestamp
        test_message = "Real timestamp test"
        terminal.add_log_message(test_message)

        # Verify formatted message has correct structure
        mock_insert_text.assert_called_once()
        formatted_message = mock_insert_text.call_args[0][0]

        # Check message format: [HH:MM:SS] message\n
        timestamp_pattern = r"^\[\d{2}:\d{2}:\d{2}\] Real timestamp test\n$"
        assert re.match(timestamp_pattern, formatted_message), (
            f"Unexpected format: {formatted_message}"
        )


class TestActionButtonsFrame:
    """Test cases for ActionButtonsFrame class."""

    def test_constructor(self, qtbot: QtBot, mocker: MockerFixture) -> None:
        """Test ActionButtonsFrame constructor initializes correctly.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock the setup_ui method to isolate constructor testing
        mock_setup_ui = mocker.patch.object(ActionButtonsFrame, "setup_ui")

        # Create ActionButtonsFrame instance
        action_frame = ActionButtonsFrame()
        qtbot.addWidget(action_frame)

        # Verify setup method was called
        mock_setup_ui.assert_called_once()

    def test_setup_ui(self, qtbot: QtBot) -> None:
        """Test ActionButtonsFrame setup_ui creates UI components correctly.

        :param qtbot: pytest-qt fixture for testing Qt applications
        """
        # Create ActionButtonsFrame instance
        action_frame = ActionButtonsFrame()
        qtbot.addWidget(action_frame)

        # Verify frame style was set
        assert action_frame.frameStyle() == action_frame.Shape.Box

        # Find the create button by its text - use QPushButton directly
        buttons = action_frame.findChildren(QPushButton)
        create_button = None
        for button in buttons:
            if button.text() == "Create":
                create_button = button
                break

        # Verify create button exists and has correct properties
        assert create_button is not None, "Create button should exist"
        assert create_button.text() == "Create"
        assert create_button.minimumHeight() == 30

        # Verify button has the expected styling (check for key style properties)
        style_sheet = create_button.styleSheet()
        assert "#4CAF50" in style_sheet  # Background color
        assert "white" in style_sheet  # Text color
        assert "border-radius: 4px" in style_sheet  # Border radius

    def test_on_create_clicked_with_incomplete_tasks(
        self, qtbot: QtBot, mocker: MockerFixture
    ) -> None:
        """Test on_create_clicked when there are incomplete required tasks.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Create ActionButtonsFrame instance
        action_frame = ActionButtonsFrame()
        qtbot.addWidget(action_frame)

        # Mock the window() method to return a fake MainWindow
        mock_main_window = mocker.MagicMock()
        mock_task_list = mocker.MagicMock()
        mock_main_window.task_list = mock_task_list

        # Create mock incomplete tasks
        mock_task1 = mocker.MagicMock()
        mock_task1.description = "Set project name"
        mock_task2 = mocker.MagicMock()
        mock_task2.description = "Set project description"
        incomplete_tasks = [mock_task1, mock_task2]

        mock_task_list.get_incomplete_required_tasks.return_value = incomplete_tasks
        mocker.patch.object(action_frame, "window", return_value=mock_main_window)

        # Mock the show_incomplete_tasks_dialog method
        mock_show_dialog = mocker.patch.object(
            action_frame, "show_incomplete_tasks_dialog"
        )

        # Call on_create_clicked
        action_frame.on_create_clicked()

        # Verify get_incomplete_required_tasks was called
        mock_task_list.get_incomplete_required_tasks.assert_called_once()

        # Verify show_incomplete_tasks_dialog was called with incomplete tasks
        mock_show_dialog.assert_called_once_with(incomplete_tasks)

    def test_on_create_clicked_with_all_tasks_complete(
        self, qtbot: QtBot, mocker: MockerFixture
    ) -> None:
        """Test on_create_clicked when all required tasks are completed.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock logging to capture log messages
        mock_logging = mocker.patch("new_python_github_project.main_window.logging")

        # Create ActionButtonsFrame instance
        action_frame = ActionButtonsFrame()
        qtbot.addWidget(action_frame)

        # Mock the window() method to return a fake MainWindow
        mock_main_window = mocker.MagicMock()
        mock_task_list = mocker.MagicMock()
        mock_main_window.task_list = mock_task_list

        # No incomplete tasks (all completed)
        mock_task_list.get_incomplete_required_tasks.return_value = []
        mocker.patch.object(action_frame, "window", return_value=mock_main_window)

        # Mock the show_incomplete_tasks_dialog method
        mock_show_dialog = mocker.patch.object(
            action_frame, "show_incomplete_tasks_dialog"
        )

        # Call on_create_clicked
        action_frame.on_create_clicked()

        # Verify get_incomplete_required_tasks was called
        mock_task_list.get_incomplete_required_tasks.assert_called_once()

        # Verify show_incomplete_tasks_dialog was NOT called
        mock_show_dialog.assert_not_called()

        # Verify all expected log messages were called
        expected_calls = [
            mocker.call(
                "✓ All tasks completed! Project structure creation would proceed here."
            ),
            mocker.call("📁 Creating project structure..."),
            mocker.call("📄 Generating configuration files..."),
            mocker.call("✅ Project setup complete!"),
        ]
        mock_logging.info.assert_has_calls(expected_calls)

    def test_show_incomplete_tasks_dialog(
        self, qtbot: QtBot, mocker: MockerFixture
    ) -> None:
        """Test show_incomplete_tasks_dialog displays error dialog correctly.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Create ActionButtonsFrame instance
        action_frame = ActionButtonsFrame()
        qtbot.addWidget(action_frame)

        # Mock QMessageBox.critical
        mock_critical = mocker.patch(
            "new_python_github_project.main_window.QMessageBox.critical"
        )

        # Create mock incomplete tasks
        mock_task1 = mocker.MagicMock()
        mock_task1.description = "Set project name"
        mock_task2 = mocker.MagicMock()
        mock_task2.description = "Set project description"
        incomplete_tasks = [mock_task1, mock_task2]

        # Call show_incomplete_tasks_dialog
        action_frame.show_incomplete_tasks_dialog(incomplete_tasks)

        # Verify QMessageBox.critical was called with correct arguments
        mock_critical.assert_called_once()
        args = mock_critical.call_args[0]

        # Check the arguments passed to QMessageBox.critical
        assert args[0] is action_frame  # parent
        assert args[1] == "Incomplete Tasks"  # title

        # Check the message content
        message = args[2]
        assert (
            "The following tasks require your input before creating the project:"
            in message
        )
        assert "• Set project name" in message
        assert "• Set project description" in message
        assert "Please complete these tasks and try again." in message

        # Check the button type
        assert args[3] == QMessageBox.StandardButton.Ok


class TestTaskListFrame:
    """Test cases for TaskListFrame class."""

    def test_constructor(self, qtbot: QtBot, mocker: MockerFixture) -> None:
        """Test TaskListFrame constructor initializes correctly.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock the setup_ui and load_sample_tasks methods to isolate constructor
        mock_setup_ui = mocker.patch.object(TaskListFrame, "setup_ui")
        mock_load_sample = mocker.patch.object(TaskListFrame, "load_sample_tasks")

        # Create TaskListFrame instance
        task_frame = TaskListFrame()
        qtbot.addWidget(task_frame)

        # Verify setup methods were called
        mock_setup_ui.assert_called_once()
        mock_load_sample.assert_called_once()

    def test_get_incomplete_required_tasks_with_incomplete_tasks(
        self, qtbot: QtBot, mocker: MockerFixture
    ) -> None:
        """Test get_incomplete_required_tasks returns tasks that need user input.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock setup methods to isolate testing
        mocker.patch.object(TaskListFrame, "setup_ui")
        mocker.patch.object(TaskListFrame, "load_sample_tasks")

        # Create TaskListFrame instance
        task_frame = TaskListFrame()
        qtbot.addWidget(task_frame)

        # Create mock tasks with different states
        mock_task1 = mocker.MagicMock()
        mock_task1.has_default = False  # Requires user input
        mock_task1.is_completed = False  # Not completed

        mock_task2 = mocker.MagicMock()
        mock_task2.has_default = True  # Has default, doesn't require input
        mock_task2.is_completed = False  # Not completed

        mock_task3 = mocker.MagicMock()
        mock_task3.has_default = False  # Requires user input
        mock_task3.is_completed = True  # Already completed

        mock_task4 = mocker.MagicMock()
        mock_task4.has_default = False  # Requires user input
        mock_task4.is_completed = False  # Not completed

        # Set up the all_tasks list
        task_frame.all_tasks = [mock_task1, mock_task2, mock_task3, mock_task4]

        # Call get_incomplete_required_tasks
        incomplete_tasks = task_frame.get_incomplete_required_tasks()

        # Should return only task1 and task4 (no default and not completed)
        assert len(incomplete_tasks) == 2
        assert mock_task1 in incomplete_tasks
        assert mock_task4 in incomplete_tasks
        assert mock_task2 not in incomplete_tasks  # Has default
        assert mock_task3 not in incomplete_tasks  # Already completed

    def test_get_incomplete_required_tasks_with_all_tasks_complete(
        self, qtbot: QtBot, mocker: MockerFixture
    ) -> None:
        """Test get_incomplete_required_tasks returns empty list when all tasks complete.

        :param qtbot: pytest-qt fixture for testing Qt applications
        :param mocker: pytest-mock fixture for mocking dependencies
        """
        # Mock setup methods to isolate testing
        mocker.patch.object(TaskListFrame, "setup_ui")
        mocker.patch.object(TaskListFrame, "load_sample_tasks")

        # Create TaskListFrame instance
        task_frame = TaskListFrame()
        qtbot.addWidget(task_frame)

        # Create mock tasks where all are either completed or have defaults
        mock_task1 = mocker.MagicMock()
        mock_task1.has_default = False  # Requires user input
        mock_task1.is_completed = True  # But completed

        mock_task2 = mocker.MagicMock()
        mock_task2.has_default = True  # Has default
        mock_task2.is_completed = False  # Not completed (but doesn't matter)

        mock_task3 = mocker.MagicMock()
        mock_task3.has_default = True  # Has default
        mock_task3.is_completed = True  # Completed

        # Set up the all_tasks list
        task_frame.all_tasks = [mock_task1, mock_task2, mock_task3]

        # Call get_incomplete_required_tasks
        incomplete_tasks = task_frame.get_incomplete_required_tasks()

        # Should return empty list since no tasks require user input and are incomplete
        assert len(incomplete_tasks) == 0
        assert incomplete_tasks == []
