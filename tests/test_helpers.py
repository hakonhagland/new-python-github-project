"""Tests for helpers module."""

import logging
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import click
import pytest
from PyQt6.QtWidgets import QApplication
from pytest_mock.plugin import MockerFixture

from new_python_github_project import helpers
from new_python_github_project.config import Config
from new_python_github_project.exceptions import ConfigException

from .common import GetConfig


class TestCheckAnotherInstanceRunning:
    """Test check_another_instance_running function."""

    def test_no_lockfile_exists(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test when no lockfile exists."""
        config = get_config()
        mock_lockfile = mocker.patch.object(config, "get_lockfile_path")
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_lockfile.return_value = mock_path

        # Should not raise exception
        helpers.check_another_instance_running(config)

    def test_lockfile_exists_but_process_not_running(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test when lockfile exists but process is not running."""
        config = get_config()
        mock_lockfile = mocker.patch.object(config, "get_lockfile_path")
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_lockfile.return_value = mock_path

        # Mock file operations
        mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="12345"))
        mock_kill = mocker.patch("os.kill", side_effect=OSError("No such process"))
        mock_remove = mocker.patch.object(config, "remove_lockfile")

        helpers.check_another_instance_running(config)

        mock_kill.assert_called_once_with(12345, 0)
        mock_remove.assert_called_once()

    def test_lockfile_exists_and_process_running(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test when lockfile exists and process is running."""
        config = get_config()
        mock_lockfile = mocker.patch.object(config, "get_lockfile_path")
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_lockfile.return_value = mock_path

        # Mock file operations
        mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="12345"))
        mock_kill = mocker.patch("os.kill", return_value=None)  # Process exists
        mock_exit = mocker.patch("sys.exit")

        helpers.check_another_instance_running(config)

        mock_kill.assert_called_once_with(12345, 0)
        mock_exit.assert_called_once_with(1)

    def test_lockfile_invalid_content(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test when lockfile contains invalid content."""
        config = get_config()
        mock_lockfile = mocker.patch.object(config, "get_lockfile_path")
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_lockfile.return_value = mock_path

        # Mock file operations
        mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data="invalid"))
        mock_remove = mocker.patch.object(config, "remove_lockfile")

        helpers.check_another_instance_running(config)

        mock_remove.assert_called_once()

    def test_lockfile_read_error(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test when lockfile cannot be read."""
        config = get_config()
        mock_lockfile = mocker.patch.object(config, "get_lockfile_path")
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_lockfile.return_value = mock_path

        # Mock file operations to raise exception
        mock_open = mocker.patch(
            "builtins.open", side_effect=OSError("Permission denied")
        )
        mock_remove = mocker.patch.object(config, "remove_lockfile")

        helpers.check_another_instance_running(config)

        mock_remove.assert_called_once()


class TestCreateQApplication:
    """Test create_qapplication function."""

    def test_creates_qapplication_with_correct_settings(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test that create_qapplication creates app with correct settings."""
        config = get_config()

        # Mock QApplication and related classes
        mock_app = MagicMock(spec=QApplication)
        mock_qapp_class = mocker.patch(
            "new_python_github_project.helpers.QApplication", return_value=mock_app
        )
        mock_load_icons = mocker.patch("new_python_github_project.helpers._load_icons")
        mocker.patch("platform.system", return_value="Linux")

        result = helpers.create_qapplication(config)

        mock_qapp_class.assert_called_once_with(sys.argv)
        mock_app.setStyle.assert_called_once_with("Fusion")
        mock_app.setQuitOnLastWindowClosed.assert_called_once_with(False)
        mock_load_icons.assert_called_once_with(mock_app, config)
        mock_app.setApplicationDisplayName.assert_called_once_with(
            "New Python GitHub Project"
        )
        mock_app.setApplicationName.assert_called_once_with("New Python GitHub Project")
        mock_app.setOrganizationName.assert_called_once_with("hakonhagland")
        mock_app.setOrganizationDomain.assert_called_once_with("github.com")
        mock_app.setApplicationVersion.assert_called_once_with("1.0.0")
        mock_app.aboutToQuit.connect.assert_called_once_with(config.remove_lockfile)
        assert result == mock_app

    def test_non_macos_platform(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test create_qapplication on non-macOS platform."""
        config = get_config()

        mock_app = MagicMock(spec=QApplication)
        mock_qapp_class = mocker.patch(
            "new_python_github_project.helpers.QApplication", return_value=mock_app
        )
        mock_load_icons = mocker.patch("new_python_github_project.helpers._load_icons")
        mock_fix_macos = mocker.patch(
            "new_python_github_project.helpers._fix_macos_app_name"
        )
        mocker.patch("platform.system", return_value="Linux")

        helpers.create_qapplication(config)

        # _fix_macos_app_name should not be called on non-macOS
        mock_fix_macos.assert_not_called()


class TestDaemonize:
    """Test daemonize function."""

    def test_windows_platform(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test daemonize on Windows platform."""
        config = get_config()

        mocker.patch("platform.system", return_value="Windows")
        mock_get_logfile = mocker.patch.object(
            config, "get_logfile_path", return_value=Path("/fake/log.txt")
        )
        mock_setup_logging = mocker.patch(
            "new_python_github_project.helpers._setup_daemon_logging"
        )

        helpers.daemonize(config, verbose=True)

        mock_get_logfile.assert_called_once()
        mock_setup_logging.assert_called_once_with(str(Path("/fake/log.txt")), True)

    def test_windows_platform_with_original_cwd(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test daemonize on Windows platform with original_cwd parameter."""
        config = get_config()

        mocker.patch("platform.system", return_value="Windows")
        mock_get_logfile = mocker.patch.object(
            config, "get_logfile_path", return_value=Path("/fake/log.txt")
        )
        mock_setup_logging = mocker.patch(
            "new_python_github_project.helpers._setup_daemon_logging"
        )

        original_cwd = "/original/working/directory"
        helpers.daemonize(config, verbose=True, original_cwd=original_cwd)

        # Verify original_cwd was stored in config
        assert config.original_cwd == original_cwd
        mock_get_logfile.assert_called_once()
        mock_setup_logging.assert_called_once_with(str(Path("/fake/log.txt")), True)


class TestDebugToFile:
    """Test debug_to_file function."""

    def test_writes_debug_info_to_file(self, mocker: MockerFixture) -> None:
        """Test that debug_to_file writes JSON debug info to file."""
        # Mock datetime import inside the function
        mock_datetime = MagicMock()
        mock_datetime.datetime.now.return_value.isoformat.return_value = (
            "2023-01-01T12:00:00"
        )

        mock_getpid = mocker.patch("os.getpid", return_value=12345)
        mock_getppid = mocker.patch("os.getppid", return_value=54321)
        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        # Mock the import inside the function
        with patch(
            "builtins.__import__",
            side_effect=lambda name, *args: mock_datetime
            if name == "datetime"
            else __import__(name, *args),
        ):
            helpers.debug_to_file("test message", {"key": "value"}, "/tmp/test.log")

        mock_open.assert_called_once_with("/tmp/test.log", "a")
        handle = mock_open.return_value.__enter__.return_value
        handle.write.assert_called_once()
        written_content = handle.write.call_args[0][0]
        assert "test message" in written_content
        assert '"key": "value"' in written_content

    def test_writes_debug_info_without_data(self, mocker: MockerFixture) -> None:
        """Test debug_to_file without additional data."""
        # Mock datetime import inside the function
        mock_datetime = MagicMock()
        mock_datetime.datetime.now.return_value.isoformat.return_value = (
            "2023-01-01T12:00:00"
        )

        mock_getpid = mocker.patch("os.getpid", return_value=12345)
        mock_getppid = mocker.patch("os.getppid", return_value=54321)
        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        # Mock the import inside the function
        with patch(
            "builtins.__import__",
            side_effect=lambda name, *args: mock_datetime
            if name == "datetime"
            else __import__(name, *args),
        ):
            helpers.debug_to_file("test message only")

        mock_open.assert_called_once_with("/tmp/pyqt_debug.log", "a")

    def test_handles_file_write_exception(self, mocker: MockerFixture) -> None:
        """Test debug_to_file handles file write exceptions."""
        # Mock datetime import inside the function
        mock_datetime = MagicMock()
        mock_datetime.datetime.now.return_value.isoformat.return_value = (
            "2023-01-01T12:00:00"
        )

        mock_getpid = mocker.patch("os.getpid", return_value=12345)
        mock_getppid = mocker.patch("os.getppid", return_value=54321)
        mock_open = mocker.patch(
            "builtins.open", side_effect=OSError("Permission denied")
        )
        mock_print = mocker.patch("builtins.print")

        # Mock the import inside the function
        with patch(
            "builtins.__import__",
            side_effect=lambda name, *args: mock_datetime
            if name == "datetime"
            else __import__(name, *args),
        ):
            helpers.debug_to_file("test message")

        mock_print.assert_called_once()
        assert "DEBUG ERROR" in str(mock_print.call_args)


class TestDetachFromTerminal:
    """Test detach_from_terminal function."""

    def test_windows_attached_to_console(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test detach_from_terminal on Windows when attached to console."""
        config = get_config()
        ctx = MagicMock(spec=click.Context)

        mocker.patch("platform.system", return_value="Windows")
        mock_is_attached = mocker.patch(
            "new_python_github_project.helpers._is_attached_to_console",
            return_value=True,
        )
        mock_detach = mocker.patch(
            "new_python_github_project.helpers._detach_from_console_windows"
        )
        mock_write_lockfile = mocker.patch.object(config, "write_lockfile")

        helpers.detach_from_terminal(config, ctx)

        mock_is_attached.assert_called_once()
        mock_detach.assert_called_once_with(config, ctx)

    def test_windows_not_attached_to_console(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test detach_from_terminal on Windows when not attached to console."""
        config = get_config()
        ctx = MagicMock(spec=click.Context)

        mocker.patch("platform.system", return_value="Windows")
        mock_is_attached = mocker.patch(
            "new_python_github_project.helpers._is_attached_to_console",
            return_value=False,
        )
        mock_detach = mocker.patch(
            "new_python_github_project.helpers._detach_from_console_windows"
        )
        mock_write_lockfile = mocker.patch.object(config, "write_lockfile")

        helpers.detach_from_terminal(config, ctx)

        mock_is_attached.assert_called_once()
        mock_detach.assert_not_called()
        mock_write_lockfile.assert_called_once()

    def test_macos_platform(self, get_config: GetConfig, mocker: MockerFixture) -> None:
        """Test detach_from_terminal on macOS platform."""
        config = get_config()
        ctx = MagicMock(spec=click.Context)

        mocker.patch("platform.system", return_value="Darwin")
        mock_detach_macos = mocker.patch(
            "new_python_github_project.helpers._detach_macos_gui"
        )
        mock_write_lockfile = mocker.patch.object(config, "write_lockfile")

        helpers.detach_from_terminal(config, ctx)

        mock_detach_macos.assert_called_once_with(config, ctx)
        mock_write_lockfile.assert_called_once()

    def test_linux_attached_to_terminal(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test detach_from_terminal on Linux when attached to terminal."""
        config = get_config()
        ctx = MagicMock(spec=click.Context)
        ctx.obj = {"VERBOSE": True}

        mocker.patch("platform.system", return_value="Linux")
        # Mock Unix-specific functions that may not exist on Windows
        mock_getpgrp = mocker.patch("os.getpgrp", return_value=12345, create=True)
        mock_tcgetpgrp = mocker.patch(
            "os.tcgetpgrp", return_value=12345, create=True
        )  # Same = attached
        mock_daemonize = mocker.patch("new_python_github_project.helpers.daemonize")
        mock_write_lockfile = mocker.patch.object(config, "write_lockfile")

        helpers.detach_from_terminal(config, ctx)

        mock_daemonize.assert_called_once_with(config, True, mocker.ANY)
        mock_write_lockfile.assert_called_once()

    def test_linux_not_attached_to_terminal(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test detach_from_terminal on Linux when not attached to terminal."""
        config = get_config()
        ctx = MagicMock(spec=click.Context)

        mocker.patch("platform.system", return_value="Linux")
        # Mock Unix-specific functions that may not exist on Windows
        mock_getpgrp = mocker.patch("os.getpgrp", return_value=12345, create=True)
        mock_tcgetpgrp = mocker.patch(
            "os.tcgetpgrp", return_value=54321, create=True
        )  # Different = not attached
        mock_daemonize = mocker.patch("new_python_github_project.helpers.daemonize")
        mock_write_lockfile = mocker.patch.object(config, "write_lockfile")

        helpers.detach_from_terminal(config, ctx)

        mock_daemonize.assert_not_called()
        mock_write_lockfile.assert_called_once()


class TestEditConfigFile:
    """Test edit_config_file function."""

    def test_linux_platform(self, get_config: GetConfig, mocker: MockerFixture) -> None:
        """Test edit_config_file on Linux platform."""
        config = get_config()
        # Mock the config structure properly
        mock_config_data = {
            "Editor": {"Linux": "gedit", "MacOS": "TextEdit", "Windows": "notepad"}
        }
        mocker.patch.object(config, "config", mock_config_data)

        mock_get_config_file = mocker.patch.object(
            config, "get_config_file", return_value=Path("/fake/config.ini")
        )
        mocker.patch("platform.system", return_value="Linux")
        mock_popen = mocker.patch("subprocess.Popen")

        helpers.edit_config_file(config)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == ["gedit", str(Path("/fake/config.ini"))]

    def test_macos_platform(self, get_config: GetConfig, mocker: MockerFixture) -> None:
        """Test edit_config_file on macOS platform."""
        config = get_config()
        # Mock the config structure properly
        mock_config_data = {
            "Editor": {"Linux": "gedit", "MacOS": "TextEdit", "Windows": "notepad"}
        }
        mocker.patch.object(config, "config", mock_config_data)

        mock_get_config_file = mocker.patch.object(
            config, "get_config_file", return_value=Path("/fake/config.ini")
        )
        mocker.patch("platform.system", return_value="Darwin")
        mock_popen = mocker.patch("subprocess.Popen")

        helpers.edit_config_file(config)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == ["open", "-a", "TextEdit", str(Path("/fake/config.ini"))]

    def test_windows_platform(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test edit_config_file on Windows platform."""
        config = get_config()
        # Mock the config structure properly
        mock_config_data = {
            "Editor": {"Linux": "gedit", "MacOS": "TextEdit", "Windows": "notepad"}
        }
        mocker.patch.object(config, "config", mock_config_data)

        mock_get_config_file = mocker.patch.object(
            config, "get_config_file", return_value=Path("/fake/config.ini")
        )
        mocker.patch("platform.system", return_value="Windows")
        mock_popen = mocker.patch("subprocess.Popen")

        helpers.edit_config_file(config)

        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == ["notepad", str(Path("/fake/config.ini"))]

    def test_unknown_platform(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test edit_config_file on unknown platform."""
        config = get_config()
        # Mock the config structure properly
        mock_config_data = {
            "Editor": {"Linux": "gedit", "MacOS": "TextEdit", "Windows": "notepad"}
        }
        mocker.patch.object(config, "config", mock_config_data)

        mock_get_config_file = mocker.patch.object(
            config, "get_config_file", return_value=Path("/fake/config.ini")
        )
        mocker.patch("platform.system", return_value="UnknownOS")

        with pytest.raises(ConfigException):
            helpers.edit_config_file(config)

    def test_editor_not_found(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test edit_config_file when editor is not found."""
        config = get_config()
        # Mock the config structure properly
        mock_config_data = {
            "Editor": {
                "Linux": "nonexistent-editor",
                "MacOS": "TextEdit",
                "Windows": "notepad",
            }
        }
        mocker.patch.object(config, "config", mock_config_data)

        mock_get_config_file = mocker.patch.object(
            config, "get_config_file", return_value=Path("/fake/config.ini")
        )
        mocker.patch("platform.system", return_value="Linux")
        mock_popen = mocker.patch(
            "subprocess.Popen", side_effect=FileNotFoundError("No such file")
        )

        # Should not raise exception
        helpers.edit_config_file(config)


class TestLocateHicolorIcons:
    """Test locate_hicolor_icons function."""

    def test_icons_directory_exists(self, mocker: MockerFixture) -> None:
        """Test locate_hicolor_icons when icons directory exists."""
        mock_sysconfig = mocker.patch("sysconfig.get_paths")
        mock_sysconfig.return_value = {"data": "/usr/local"}

        # Mock pathlib.Path.is_dir at class level
        mock_path_is_dir = mocker.patch("pathlib.Path.is_dir", return_value=True)

        result = helpers.locate_hicolor_icons()

        mock_path_is_dir.assert_called_once()
        assert result == Path("/usr/local/share/icons/hicolor")

    def test_icons_directory_not_exists(self, mocker: MockerFixture) -> None:
        """Test locate_hicolor_icons when icons directory does not exist."""
        mock_sysconfig = mocker.patch("sysconfig.get_paths")
        mock_sysconfig.return_value = {"data": "/usr/local"}

        # Mock pathlib.Path.is_dir at class level
        mock_path_is_dir = mocker.patch("pathlib.Path.is_dir", return_value=False)

        result = helpers.locate_hicolor_icons()

        mock_path_is_dir.assert_called_once()
        assert result is None


class TestSetupRemoteDebugging:
    """Test setup_remote_debugging function."""

    def test_debugpy_available(self, mocker: MockerFixture) -> None:
        """Test setup_remote_debugging when debugpy is available."""
        mock_debugpy = MagicMock()
        mock_import = mocker.patch("builtins.__import__", return_value=mock_debugpy)
        mock_debug_to_file = mocker.patch(
            "new_python_github_project.helpers.debug_to_file"
        )
        mock_print = mocker.patch("builtins.print")

        helpers.setup_remote_debugging("127.0.0.1", 9999)

        mock_debugpy.listen.assert_called_once_with(("127.0.0.1", 9999))
        mock_debug_to_file.assert_called_once_with(
            "Remote debugging enabled on 127.0.0.1:9999"
        )
        assert mock_print.call_count == 2

    def test_debugpy_not_available(self, mocker: MockerFixture) -> None:
        """Test setup_remote_debugging when debugpy is not available."""
        mock_import = mocker.patch(
            "builtins.__import__", side_effect=ImportError("No module named 'debugpy'")
        )
        mock_debug_to_file = mocker.patch(
            "new_python_github_project.helpers.debug_to_file"
        )
        mock_print = mocker.patch("builtins.print")

        helpers.setup_remote_debugging()

        mock_debug_to_file.assert_called_once_with(
            "debugpy not installed. Install with: pip install debugpy"
        )
        mock_print.assert_called_once_with(
            "debugpy not installed. Install with: pip install debugpy"
        )


# Tests for private functions
# Note: Platform-specific functions (_detach_from_console_windows, _detach_macos_gui,
# _fix_macos_app_name, _is_attached_to_console, _load_windows_icon) are excluded
# from testing using # pragma: no cover comments because they require platform-specific
# environments and system calls that are difficult to test in a cross-platform CI environment.


class TestLoadIcons:
    """Test _load_icons function (excluding Windows-specific behavior)."""

    def test_linux_platform(self, get_config: GetConfig, mocker: MockerFixture) -> None:
        """Test _load_icons on Linux platform."""
        config = get_config()
        app = MagicMock(spec=QApplication)

        mocker.patch("platform.system", return_value="Linux")
        mock_set_desktop_filename = mocker.patch(
            "new_python_github_project.helpers.QGuiApplication.setDesktopFileName"
        )
        mock_locate_icons = mocker.patch(
            "new_python_github_project.helpers.locate_hicolor_icons",
            return_value=Path("/usr/share/icons/hicolor"),
        )
        mock_icon_from_theme = mocker.patch(
            "new_python_github_project.helpers.QIcon.fromTheme"
        )
        mock_icon = MagicMock()
        mock_icon.isNull.return_value = False
        mock_icon_from_theme.return_value = mock_icon

        helpers._load_icons(app, config)

        mock_set_desktop_filename.assert_called_once_with(config.appname)
        app.setWindowIcon.assert_called_once_with(mock_icon)

    def test_other_platform_with_icons_found(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test _load_icons on other platforms when icons are found."""
        config = get_config()
        app = MagicMock(spec=QApplication)

        mocker.patch("platform.system", return_value="Darwin")  # macOS
        mock_locate_icons = mocker.patch(
            "new_python_github_project.helpers.locate_hicolor_icons",
            return_value=Path("/usr/share/icons/hicolor"),
        )
        mock_icon = MagicMock()
        mock_icon.isNull.return_value = False
        mock_icon_from_theme = mocker.patch(
            "new_python_github_project.helpers.QIcon.fromTheme", return_value=mock_icon
        )

        helpers._load_icons(app, config)

        app.setWindowIcon.assert_called_once_with(mock_icon)

    def test_other_platform_no_icons_found(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test _load_icons on other platforms when no icons are found."""
        config = get_config()
        app = MagicMock(spec=QApplication)

        mocker.patch("platform.system", return_value="Darwin")  # macOS
        mock_locate_icons = mocker.patch(
            "new_python_github_project.helpers.locate_hicolor_icons", return_value=None
        )
        mock_icon = MagicMock()
        mock_icon_from_theme = mocker.patch(
            "new_python_github_project.helpers.QIcon.fromTheme", return_value=mock_icon
        )

        helpers._load_icons(app, config)

        mock_icon_from_theme.assert_called_with("applications-python")
        app.setWindowIcon.assert_called_once_with(mock_icon)

    def test_other_platform_icon_null_fallback(
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test _load_icons fallback when icon is null."""
        config = get_config()
        app = MagicMock(spec=QApplication)

        mocker.patch("platform.system", return_value="Darwin")  # macOS
        mock_locate_icons = mocker.patch(
            "new_python_github_project.helpers.locate_hicolor_icons",
            return_value=Path("/usr/share/icons/hicolor"),
        )

        # First call returns null icon, second call returns fallback
        mock_null_icon = MagicMock()
        mock_null_icon.isNull.return_value = True
        mock_fallback_icon = MagicMock()
        mock_icon_from_theme = mocker.patch(
            "new_python_github_project.helpers.QIcon.fromTheme",
            side_effect=[mock_null_icon, mock_fallback_icon],
        )

        helpers._load_icons(app, config)

        # Should be called twice: once for appname, once for fallback
        assert mock_icon_from_theme.call_count == 2
        app.setWindowIcon.assert_called_once_with(mock_fallback_icon)


class TestSetupDaemonLogging:
    """Test _setup_daemon_logging function."""

    def test_setup_daemon_logging_verbose(self, mocker: MockerFixture) -> None:
        """Test _setup_daemon_logging with verbose=True."""
        mock_root_logger = MagicMock()
        mock_get_logger = mocker.patch(
            "logging.getLogger", return_value=mock_root_logger
        )
        mock_file_handler_class = mocker.patch("logging.FileHandler")
        mock_file_handler = MagicMock()
        mock_file_handler_class.return_value = mock_file_handler
        mock_formatter_class = mocker.patch("logging.Formatter")
        mock_formatter = MagicMock()
        mock_formatter_class.return_value = mock_formatter

        helpers._setup_daemon_logging("/fake/log.txt", verbose=True)

        mock_get_logger.assert_called_once_with()
        mock_file_handler_class.assert_called_once_with("/fake/log.txt", mode="a")
        mock_file_handler.setFormatter.assert_called_once_with(mock_formatter)
        mock_root_logger.addHandler.assert_called_once_with(mock_file_handler)
        mock_root_logger.setLevel.assert_called_once_with(logging.INFO)

    def test_setup_daemon_logging_not_verbose(self, mocker: MockerFixture) -> None:
        """Test _setup_daemon_logging with verbose=False."""
        mock_root_logger = MagicMock()
        mock_get_logger = mocker.patch(
            "logging.getLogger", return_value=mock_root_logger
        )
        mock_file_handler_class = mocker.patch("logging.FileHandler")
        mock_file_handler = MagicMock()
        mock_file_handler_class.return_value = mock_file_handler
        mock_formatter_class = mocker.patch("logging.Formatter")
        mock_formatter = MagicMock()
        mock_formatter_class.return_value = mock_formatter

        helpers._setup_daemon_logging("/fake/log.txt", verbose=False)

        mock_get_logger.assert_called_once_with()
        mock_file_handler_class.assert_called_once_with("/fake/log.txt", mode="a")
        mock_file_handler.setFormatter.assert_called_once_with(mock_formatter)
        mock_root_logger.addHandler.assert_called_once_with(mock_file_handler)
        mock_root_logger.setLevel.assert_called_once_with(logging.WARNING)

    def test_setup_daemon_logging_removes_existing_handlers(
        self, mocker: MockerFixture
    ) -> None:
        """Test _setup_daemon_logging removes existing handlers."""
        # Create mock handlers to test the removal loop
        mock_handler1 = MagicMock()
        mock_handler2 = MagicMock()
        existing_handlers = [mock_handler1, mock_handler2]

        mock_root_logger = MagicMock()
        mock_root_logger.handlers = existing_handlers
        mock_get_logger = mocker.patch(
            "logging.getLogger", return_value=mock_root_logger
        )
        mock_file_handler_class = mocker.patch("logging.FileHandler")
        mock_file_handler = MagicMock()
        mock_file_handler_class.return_value = mock_file_handler
        mock_formatter_class = mocker.patch("logging.Formatter")
        mock_formatter = MagicMock()
        mock_formatter_class.return_value = mock_formatter

        helpers._setup_daemon_logging("/fake/log.txt", verbose=False)

        # Verify existing handlers were removed
        assert mock_root_logger.removeHandler.call_count == 2
        mock_root_logger.removeHandler.assert_any_call(mock_handler1)
        mock_root_logger.removeHandler.assert_any_call(mock_handler2)
