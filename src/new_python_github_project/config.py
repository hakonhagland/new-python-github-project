import configparser
import importlib.resources
import logging
import os
import shutil
import typing

from configparser import ConfigParser
from pathlib import Path

import platformdirs

from new_python_github_project.exceptions import ConfigException
from new_python_github_project.constants import Directories, FileNames


class Config:
    # NOTE: These are made class variables since they must be accessible from
    #   pytest before creating an object of this class
    appname = "new-python-github-project"
    config_fn = "config.ini"
    dirlock_fn = ".dirlock"
    lockfile_fn = "app.lock"
    logfile_fn = "app.log"
    dirlock_string = "author=HH"

    def __init__(self) -> None:
        self.config_dir = self.get_config_dir()
        self.config_path = Path(self.config_dir) / self.config_fn
        logging.info(f"Config directory: {str(self.config_dir)}")
        logging.info(f"Config file: {str(self.config_path)}")
        logging.info("Reading config file...")
        self.read_config()
        logging.info("Config read")

    def check_correct_config_dir(self, lock_file: Path) -> None:
        """The config dir might be owned by another app with the same name"""
        if lock_file.exists():
            if lock_file.is_file():
                with open(str(lock_file), encoding="utf_8") as fp:
                    line = fp.readline()
                    if line.startswith(self.dirlock_string):
                        return
                msg = "bad content"
            else:
                msg = "is a directory"
        else:
            msg = "missing"
        raise ConfigException(
            f"Unexpected: Config dir lock file: {msg}. "
            f"The data directory {str(lock_file.parent)} might be owned by another app."
        )

    def copy_default_config(self, path: Path) -> None:
        """Copy the default config file to the given path."""
        logging.info(f"Copying default config file to: {str(path)}")
        default_config = importlib.resources.files(
            "new_python_github_project.data"
        ).joinpath("default_config.ini")
        shutil.copyfile(str(default_config), str(path))

    def get_config_dir(self) -> Path:
        config_dir = platformdirs.user_config_dir(appname=self.appname)
        path = Path(config_dir)
        lock_file = path / self.dirlock_fn
        if path.exists():
            if path.is_file():
                raise ConfigException(
                    f"Config directory {str(path)} is file. Expected directory"
                )
            self.check_correct_config_dir(lock_file)
        else:
            path.mkdir(parents=True)
            with open(str(lock_file), "a", encoding="utf_8") as fp:
                fp.write(self.dirlock_string)
        return path

    def get_config_file(self) -> Path:
        return self.config_path

    def get_lockfile_path(self) -> Path:
        return self.config_dir / self.lockfile_fn

    def get_logfile_path(self) -> Path:
        return self.config_dir / self.logfile_fn

    def get_pyproject_template(self) -> str:
        """Get the pyproject.toml template. If no template is found in the user config directory at path
        <user_config_dir>/templates/pyproject.toml, a default template is used and copied to the user config
        directory. The template should use placeholders for the project name, description, author name, author
        email, and python version. The placeholders should be on the form %%<PLACEHOLDER_NAME>%%, where
        PLACEHOLDER_NAME is one of the following: PROJECT_NAME,
        PROJECT_DESCRIPTION, AUTHOR_NAME, AUTHOR_EMAIL, and PYTHON_VERSION. For example, the template should contain
        the line "name = %%PROJECT_NAME%%" and "description = %%PROJECT_DESCRIPTION%%".
        The template should be a valid pyproject.toml file.
        """
        dir_ = self.get_config_dir()
        template_dir = dir_ / Directories.templates
        if not template_dir.exists():
            template_dir.mkdir(parents=True)
        filename = FileNames.pyproject_toml
        path = template_dir / filename
        if not path.exists():
            template = ""
            logging.info(
                f"No template found for {filename}. Looking for a default template..."
            )
            default_path = importlib.resources.files(
                "new_python_github_project.data.templates"
            ).joinpath(filename)
            default_path = typing.cast(Path, default_path)
            if not default_path.exists():
                raise ConfigException(f"No default template found for {filename}.")
            # Read the default template
            with open(str(default_path), "r", encoding="utf_8") as fp:
                template = fp.read()
            # Copy the template to user config dir
            with open(path, "w", encoding="utf_8") as fp:
                fp.write(template)
        else:
            # Read the template
            with open(path, "r", encoding="utf_8") as fp:
                template = fp.read()
        return template

    def read_config(self) -> None:
        path = self.get_config_file()
        if path.exists():
            if not path.is_file():
                raise ConfigException(
                    f"Config filename {str(path)} exists, but filetype is not file"
                )
        else:
            self.copy_default_config(path)
        config = configparser.ConfigParser(
            # See https://stackoverflow.com/a/53274707/2173773
            converters={"list": lambda x: [i.strip() for i in x.split(",")]}
        )
        self.read_defaults(config)
        config.read(str(path))
        logging.info(f"Read config file: {str(path)}")
        self.config = config

    def read_defaults(self, config: ConfigParser) -> None:
        path = importlib.resources.files("new_python_github_project.data").joinpath(
            "default_config.ini"
        )
        config.read(str(path))

    def remove_lockfile(self) -> None:
        """Remove the lockfile."""
        lockfile = self.get_lockfile_path()
        lockfile.unlink(missing_ok=True)

    def write_lockfile(self) -> None:
        """Write the lockfile."""
        lockfile = self.get_lockfile_path()
        lockfile.write_text(str(os.getpid()))
