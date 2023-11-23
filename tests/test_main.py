import logging

from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner

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
        assert result.stdout.startswith("Hello World!")
