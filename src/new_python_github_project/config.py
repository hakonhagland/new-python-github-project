import configparser
import importlib.resources
import logging
import shutil
from configparser import ConfigParser
from pathlib import Path

import platformdirs

from new_python_github_project.exceptions import ConfigException


class Config:
    # NOTE: These are made class variables since they must be accessible from
    #   pytest before creating an object of this class
    dirlock_fn = ".dirlock"
    config_fn = "config.ini"
    appname = "new-python-github-project"

    def __init__(self) -> None:
        self.lockfile_string = "author=HH"
        self.config_dir = self.get_config_dir()
        self.config_path = Path(self.config_dir) / self.config_fn
        self.read_config()

    def check_correct_config_dir(self, lock_file: Path) -> None:
        """The config dir might be owned by another app with the same name"""
        if lock_file.exists():
            if lock_file.is_file():
                with open(str(lock_file), encoding="utf_8") as fp:
                    line = fp.readline()
                    if line.startswith(self.lockfile_string):
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
                fp.write(self.lockfile_string)
        return path

    def get_config_file(self) -> Path:
        return self.config_path

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
