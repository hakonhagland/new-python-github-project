import shutil
from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture

from new_python_github_project.config import Config
from .common import GetConfig, PytestDataDict


# This will override all qapp_args in all tests since it is session scoped
@pytest.fixture(scope="session")
def qapp_args() -> list[str]:
    return ["new-python-github-project", "-v", "create"]


@pytest.fixture(scope="session")
def test_file_path() -> Path:
    return Path(__file__).parent / "files"


@pytest.fixture(scope="session")
def test_data() -> PytestDataDict:
    """Constants for testing."""
    return {
        "config_dir": "config",  # Directory inside test_file_path
        "data_dir": "data",  # Directory inside test_file_path
    }


@pytest.fixture()
def data_dir_path(
    tmp_path: Path, test_file_path: Path, test_data: PytestDataDict
) -> Path:
    data_dir = tmp_path / test_data["data_dir"]
    data_dir.mkdir()
    data_dirlock_fn = test_file_path / test_data["data_dir"] / Config.dirlock_fn
    shutil.copy(data_dirlock_fn, data_dir)
    return data_dir


@pytest.fixture()
def config_dir_path(
    test_file_path: Path,
    test_data: PytestDataDict,
    tmp_path: Path,
) -> Path:
    cfg_dir_src = test_file_path / test_data["config_dir"]
    cfg_dir = tmp_path / test_data["config_dir"]
    cfg_dir.mkdir()
    cfg_dirlock_fn = cfg_dir_src / Config.dirlock_fn
    shutil.copy(cfg_dirlock_fn, cfg_dir)
    cfg_fn = cfg_dir_src / Config.config_fn
    shutil.copy(cfg_fn, cfg_dir)
    return cfg_dir


@pytest.fixture()
def get_config(
    config_dir_path: Path, mocker: MockerFixture, data_dir_path: Path
) -> GetConfig:
    def _config(setup_firebase: bool = False) -> Config:
        cfg_dir = config_dir_path
        data_dir = data_dir_path
        mocker.patch(
            "new_python_github_project.config.platformdirs.user_config_dir",
            return_value=cfg_dir,
        )
        mocker.patch(
            "new_python_github_project.config.platformdirs.user_data_dir",
            return_value=data_dir,
        )
        cfg_fn = cfg_dir / Config.config_fn
        with open(str(cfg_fn), "a", encoding="utf_8") as fp:
            fp.write(str(cfg_fn))
        cfg = Config()
        return cfg

    return _config
