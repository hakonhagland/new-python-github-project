import logging
import platform
import subprocess
import sys

import click

from new_python_github_project.config import Config
from new_python_github_project.exceptions import ConfigException


def check_runtime_deps() -> bool:
    """Check that the runtime dependencies are installed."""
    return check_poetry_installed()


def check_poetry_installed() -> bool:
    dep = "poetry"
    try:
        # NOTE: poetry must be installed outside the virtual environment
        #  see https://python-poetry.org/docs/#installation
        #  This ensures that Poetry’s own dependencies will not be accidentally
        #  upgraded or uninstalled.
        subprocess.run(
            ["poetry", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        logging.error(f"Missing runtime dependency: {dep}. Please install it first")
        return False
    return True

def edit_config_file(config: Config) -> None:
    """Edit the config file."""
    config_path = config.get_config_file()
    cfg = config.config["Editor"]
    if platform.system() == "Linux":
        editor = cfg["Linux"]
        cmd = editor
        args = [str(config_path)]
    elif platform.system() == "Darwin":
        cmd = "open"
        editor = cfg["MacOS"]
        args = ["-a", editor, str(config_path)]
    elif platform.system() == "Windows":
        editor = cfg["Windows"]
        cmd = editor
        args = [str(config_path)]
    else:
        raise ConfigException(f"Unknown platform: {platform.system()}")
    logging.info(f"Running: {cmd} {args}")
    try:
        subprocess.Popen([cmd, *args], start_new_session=True)
    except FileNotFoundError as e:
        logging.error(f"{e}")
        logging.error(f"Editor not found: {editor}. Please install it first")


def read_config() -> dict:
    """Read the configuration file."""

    config = Config()
    config.read_config()
    return config


def run_init_poetry(config: Config, project_name: str) -> None:
    """Run "poetry new" to create a new project."""

    subprocess.run(
        [
            sys.executable,
            "-m",
            "poetry",
            "new",
            "--src",
            project_name,
        ]
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """``new_python_github_project`` is a command line tool for creating a new
    Python project.
    """
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)


@main.command()
@click.argument("project_name", required=True, type=str)
def create(project_name: str) -> None:
    """Create a new Python project on GitHub.

    ARGUMENTS:
    ----------

    PROJECT_NAME (str): Name of the project. This is the same as the Python module
    name. Use lowercase name with undescores and dots to separate packages and modules,
    as recommended in PEP8, do not use hyphens.

    EXAMPLES:
    ---------

    $ new-python-github-project my_module
    $ new-python-github-project my_package.my_module

    In the first example, the Python module name is "my_module" and the corresponding PyPI
    project name is "my-module". In the second example, the Python module name is
    "my_package.my_module" and the corresponding PyPI project name is "my-package-my-module".
    """
    if check_runtime_deps():
        config = read_config()
        run_init_poetry(config, project_name)
        click.echo("Hello World!")


@main.command()
@click.pass_context
def edit_config(ctx: click.Context) -> None:
    """Edit the configuration file."""
    if check_runtime_deps():
        config = read_config()
        edit_config_file(config)


if __name__ == "__main__":  # pragma: no cover
    main()
