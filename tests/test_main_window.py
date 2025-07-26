"""Unit tests for main_window.py."""

from PyQt6.QtWidgets import QApplication
from pytest_mock.plugin import MockerFixture
from pytestqt.qtbot import QtBot

from new_python_github_project.main_window import MainWindow
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
