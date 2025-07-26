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
            "new_python_github_project.main_window.setup_post_fork_logging"
        )

        # Mock the setup_ui method to isolate constructor testing
        mock_setup_ui = mocker.patch.object(MainWindow, "setup_ui")

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
