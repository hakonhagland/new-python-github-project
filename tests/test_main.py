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
            "new_python_github_project.main.subprocess.Popen",
            side_effect=FileNotFoundError,
        )
        result = main.check_runtime_deps()
        assert not result
        assert caplog.records[-1].msg.startswith(
            "Missing runtime dependency: poetry. Please install it first"
        )
