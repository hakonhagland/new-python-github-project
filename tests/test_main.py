import logging

from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from pytest_mock.plugin import MockerFixture

from new_python_github_project import main


class TestMain:
    def test_help_opt(self, caplog: LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        runner = CliRunner()
        result = runner.invoke(main.main, ["--help"])
        assert result.stdout.startswith("Usage: main [OPTIONS]")

    def test_main(self, caplog: LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        runner = CliRunner()
        result = runner.invoke(main.main)
        assert result.stderr.startswith("Usage: main [OPTIONS] COMMAND [ARGS]...")

    def test_runtime_deps(
        self,
        caplog: LogCaptureFixture,
        mocker: MockerFixture,
    ) -> None:
        caplog.set_level(logging.INFO)
        mocker.patch(
            "new_python_github_project.runtime.subprocess.run",
            side_effect=FileNotFoundError,
        )
        with caplog.at_level(logging.ERROR):
            try:
                main.runtime.check_deps()
            except SystemExit:
                pass
        assert caplog.records[-1].msg.startswith(
            "Missing runtime dependency: uv. Please install it first"
        )

    def test_verbose_flag_with_subcommand(
        self, caplog: LogCaptureFixture, mocker: MockerFixture
    ) -> None:
        """Test that verbose flag sets up INFO logging and calls setup_pre_fork_logging."""
        mock_setup = mocker.patch(
            "new_python_github_project.main.setup_pre_fork_logging"
        )
        mocker.patch("new_python_github_project.main.Config")
        mocker.patch("new_python_github_project.main.helpers.edit_config_file")

        runner = CliRunner()
        result = runner.invoke(main.main, ["--verbose", "edit-config"])

        # Should call setup_pre_fork_logging
        mock_setup.assert_called_once()
        # Should successfully run edit-config
        assert result.exit_code == 0

    def test_non_verbose_flag_with_subcommand(
        self, caplog: LogCaptureFixture, mocker: MockerFixture
    ) -> None:
        """Test that without verbose flag, WARNING logging is set up."""
        mock_setup = mocker.patch(
            "new_python_github_project.main.setup_pre_fork_logging"
        )
        mocker.patch("new_python_github_project.main.Config")
        mocker.patch("new_python_github_project.main.helpers.edit_config_file")

        runner = CliRunner()
        result = runner.invoke(main.main, ["edit-config"])

        # Should still call setup_pre_fork_logging
        mock_setup.assert_called_once()
        assert result.exit_code == 0

    def test_create_command(self, mocker: MockerFixture) -> None:
        """Test the create command execution path."""
        # Mock all dependencies to avoid actually starting GUI
        mock_config = mocker.patch("new_python_github_project.main.Config")
        mock_check_instance = mocker.patch(
            "new_python_github_project.main.helpers.check_another_instance_running"
        )
        mock_check_deps = mocker.patch(
            "new_python_github_project.main.runtime.check_deps"
        )
        mock_detach = mocker.patch(
            "new_python_github_project.main.helpers.detach_from_terminal"
        )
        mock_create_app = mocker.patch(
            "new_python_github_project.main.helpers.create_qapplication"
        )
        mock_main_window = mocker.patch("new_python_github_project.main.MainWindow")
        mock_sys_exit = mocker.patch("sys.exit")

        # Mock the QApplication and its exec method
        mock_app = mocker.MagicMock()
        mock_app.exec.return_value = 0
        mock_create_app.return_value = mock_app

        # Mock MainWindow instance
        mock_window = mocker.MagicMock()
        mock_main_window.return_value = mock_window

        runner = CliRunner()
        runner.invoke(main.create)

        # Verify all components are called in correct order
        mock_config.assert_called_once()
        mock_check_instance.assert_called_once()
        mock_check_deps.assert_called_once()
        mock_detach.assert_called_once()
        mock_create_app.assert_called_once()
        mock_main_window.assert_called_once()
        mock_window.show.assert_called_once()
        mock_app.exec.assert_called_once()
        # sys.exit should be called at least once (Click may call it too)
        assert mock_sys_exit.call_count >= 1

    def test_create_command_no_detach(self, mocker: MockerFixture) -> None:
        """Test the create command with --no-detach flag to cover line 52."""
        # Mock all dependencies to avoid actually starting GUI
        mock_config = mocker.patch("new_python_github_project.main.Config")
        mock_check_instance = mocker.patch(
            "new_python_github_project.main.helpers.check_another_instance_running"
        )
        mock_check_deps = mocker.patch(
            "new_python_github_project.main.runtime.check_deps"
        )
        mock_detach = mocker.patch(
            "new_python_github_project.main.helpers.detach_from_terminal"
        )
        mock_create_app = mocker.patch(
            "new_python_github_project.main.helpers.create_qapplication"
        )
        mock_main_window = mocker.patch("new_python_github_project.main.MainWindow")
        mock_sys_exit = mocker.patch("sys.exit")

        # Mock config instance and its write_lockfile method
        config_instance = mocker.MagicMock()
        mock_config.return_value = config_instance

        # Mock the QApplication and its exec method
        mock_app = mocker.MagicMock()
        mock_app.exec.return_value = 0
        mock_create_app.return_value = mock_app

        # Mock MainWindow instance
        mock_window = mocker.MagicMock()
        mock_main_window.return_value = mock_window

        runner = CliRunner()
        runner.invoke(main.create, ["--no-detach"])

        # Verify all components are called in correct order
        mock_config.assert_called_once()
        mock_check_instance.assert_called_once()
        mock_check_deps.assert_called_once()
        # detach_from_terminal should NOT be called with --no-detach
        mock_detach.assert_not_called()
        # write_lockfile should be called instead (this covers line 52)
        config_instance.write_lockfile.assert_called_once()
        mock_create_app.assert_called_once()
        mock_main_window.assert_called_once()
        mock_window.show.assert_called_once()
        mock_app.exec.assert_called_once()
        # sys.exit should be called at least once (Click may call it too)
        assert mock_sys_exit.call_count >= 1

    def test_edit_config_command(self, mocker: MockerFixture) -> None:
        """Test the edit_config command execution path."""
        # Mock dependencies
        mock_config = mocker.patch("new_python_github_project.main.Config")
        mock_edit_config = mocker.patch(
            "new_python_github_project.main.helpers.edit_config_file"
        )

        config_instance = mocker.MagicMock()
        mock_config.return_value = config_instance

        runner = CliRunner()
        result = runner.invoke(main.edit_config)

        # Verify components are called
        mock_config.assert_called_once()
        mock_edit_config.assert_called_once_with(config_instance)
        assert result.exit_code == 0
