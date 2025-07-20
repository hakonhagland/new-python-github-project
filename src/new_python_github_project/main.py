import logging
import sys

import click

from new_python_github_project.config import Config
from new_python_github_project import helpers
from new_python_github_project import runtime
from new_python_github_project.main_window import MainWindow


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """``new-python-gh-project`` is a command line tool for creating a new Python project."""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


@main.command()
@click.pass_context
def create(ctx: click.Context) -> None:
    """Create a new Python project on GitHub.

    This will start a GUI application that helps you create a new Python project.
    The application will run in the background, detached from the terminal.
    """
    config = Config()
    helpers.check_another_instance_running(config)
    runtime.check_deps()
    helpers.detach_from_terminal(config, ctx)
    app = helpers.create_qapplication(config)
    # All the work is done by the MainWindow callbacks
    window = MainWindow(app, config)  # noqa: F841
    window.show()
    # Start the event loop
    sys.exit(app.exec())


@main.command()
@click.pass_context
def edit_config(ctx: click.Context) -> None:
    """Edit the configuration file."""
    config = Config()
    helpers.edit_config_file(config)


if __name__ == "__main__":  # pragma: no cover
    main()
