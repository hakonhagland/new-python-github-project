import configparser
import shutil
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from pytest_mock.plugin import MockerFixture

from new_python_github_project.config import Config
from new_python_github_project.exceptions import ConfigException


@pytest.fixture()
def clean_config_fixture(tmp_path: Path, mocker: MockerFixture) -> Config:
    """Create a clean config without the conftest.py bug that appends filename."""
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir()

    # Create a clean config file (copy from test files)
    test_config_path = Path(__file__).parent / "files" / "config" / "config.ini"
    target_config_path = cfg_dir / "config.ini"
    shutil.copy(test_config_path, target_config_path)

    # Create dirlock file
    dirlock_path = cfg_dir / ".dirlock"
    dirlock_path.write_text("author=HH")

    # Mock platformdirs
    mocker.patch(
        "new_python_github_project.config.platformdirs.user_config_dir",
        return_value=str(cfg_dir),
    )

    return Config()


class TestConfig:
    """Test suite for Config class."""

    def test_class_variables(self) -> None:
        """Test that class variables are correctly set."""
        assert Config.appname == "new-python-gh-project"
        assert Config.config_fn == "config.ini"
        assert Config.dirlock_fn == ".dirlock"
        assert Config.lockfile_fn == "app.lock"
        assert Config.logfile_fn == "app.log"
        assert Config.dirlock_string == "author=HH"

    def test_init_creates_config_properly(self, clean_config_fixture: Config) -> None:
        """Test that Config initialization works properly."""
        config = clean_config_fixture
        assert isinstance(config, Config)
        assert config.config_dir.exists()
        assert config.config_path.exists()
        assert hasattr(config, "config")

    def test_check_correct_config_dir_valid_lock(self, tmp_path: Path) -> None:
        """Test check_correct_config_dir with valid lock file."""
        config = Config.__new__(Config)  # Create without __init__
        config.dirlock_string = "author=HH"

        lock_file = tmp_path / ".dirlock"
        lock_file.write_text("author=HH\n")

        # Should not raise exception
        config.check_correct_config_dir(lock_file)

    def test_check_correct_config_dir_bad_content(self, tmp_path: Path) -> None:
        """Test check_correct_config_dir with bad lock file content."""
        config = Config.__new__(Config)
        config.dirlock_string = "author=HH"

        lock_file = tmp_path / ".dirlock"
        lock_file.write_text("bad content")

        with pytest.raises(ConfigException, match="bad content"):
            config.check_correct_config_dir(lock_file)

    def test_check_correct_config_dir_is_directory(self, tmp_path: Path) -> None:
        """Test check_correct_config_dir when lock file is a directory."""
        config = Config.__new__(Config)
        config.dirlock_string = "author=HH"

        lock_file = tmp_path / ".dirlock"
        lock_file.mkdir()

        with pytest.raises(ConfigException, match="is a directory"):
            config.check_correct_config_dir(lock_file)

    def test_check_correct_config_dir_missing(self, tmp_path: Path) -> None:
        """Test check_correct_config_dir when lock file is missing."""
        config = Config.__new__(Config)
        config.dirlock_string = "author=HH"

        lock_file = tmp_path / ".dirlock"

        with pytest.raises(ConfigException, match="missing"):
            config.check_correct_config_dir(lock_file)

    def test_copy_default_config(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test copying default config file."""
        config = Config.__new__(Config)
        target_path = tmp_path / "config.ini"

        # Mock the importlib.resources behavior
        mock_files = mocker.patch("importlib.resources.files")
        mock_default_config = mocker.MagicMock()
        mock_files.return_value.joinpath.return_value = mock_default_config

        # Mock shutil.copyfile
        mock_copyfile = mocker.patch("shutil.copyfile")

        config.copy_default_config(target_path)

        mock_files.assert_called_once_with("new_python_github_project.data")
        mock_files.return_value.joinpath.assert_called_once_with("default_config.ini")
        mock_copyfile.assert_called_once_with(
            str(mock_default_config), str(target_path)
        )

    def test_get_config_dir_existing_valid_directory(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        """Test get_config_dir with existing valid directory."""
        config = Config.__new__(Config)
        config.appname = "test-app"
        config.dirlock_fn = ".dirlock"
        config.dirlock_string = "author=HH"

        # Create existing directory with valid lock file
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        lock_file = config_dir / ".dirlock"
        lock_file.write_text("author=HH")

        mocker.patch("platformdirs.user_config_dir", return_value=str(config_dir))

        result = config.get_config_dir()
        assert result == config_dir

    def test_get_config_dir_existing_file_not_directory(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        """Test get_config_dir when path exists but is a file."""
        config = Config.__new__(Config)
        config.appname = "test-app"

        # Create a file instead of directory
        config_path = tmp_path / "config"
        config_path.write_text("not a directory")

        mocker.patch("platformdirs.user_config_dir", return_value=str(config_path))

        with pytest.raises(ConfigException, match="is file. Expected directory"):
            config.get_config_dir()

    def test_get_config_dir_creates_new_directory(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        """Test get_config_dir creates new directory when it doesn't exist."""
        config = Config.__new__(Config)
        config.appname = "test-app"
        config.dirlock_fn = ".dirlock"
        config.dirlock_string = "author=HH"

        config_dir = tmp_path / "new_config"

        mocker.patch("platformdirs.user_config_dir", return_value=str(config_dir))

        result = config.get_config_dir()

        assert result == config_dir
        assert config_dir.exists()
        assert config_dir.is_dir()

        lock_file = config_dir / ".dirlock"
        assert lock_file.exists()
        assert lock_file.read_text() == "author=HH"

    def test_get_config_file(self, clean_config_fixture: Config) -> None:
        """Test get_config_file returns correct path."""
        config = clean_config_fixture
        config_file = config.get_config_file()
        assert config_file == config.config_path
        assert config_file.name == "config.ini"

    def test_get_lockfile_path(self, clean_config_fixture: Config) -> None:
        """Test get_lockfile_path returns correct path."""
        config = clean_config_fixture
        lockfile_path = config.get_lockfile_path()
        expected_path = config.config_dir / "app.lock"
        assert lockfile_path == expected_path

    def test_get_logfile_path(self, clean_config_fixture: Config) -> None:
        """Test get_logfile_path returns correct path."""
        config = clean_config_fixture
        logfile_path = config.get_logfile_path()
        expected_path = config.config_dir / "app.log"
        assert logfile_path == expected_path

    def test_get_pyproject_template_existing_template(
        self, clean_config_fixture: Config
    ) -> None:
        """Test get_pyproject_template with existing template."""
        config = clean_config_fixture

        # Create templates directory and template file
        templates_dir = config.config_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        template_file = templates_dir / "pyproject.toml"
        template_content = (
            "name = %%PROJECT_NAME%%\ndescription = %%PROJECT_DESCRIPTION%%"
        )
        template_file.write_text(template_content)

        result = config.get_pyproject_template()
        assert result == template_content

    def test_get_pyproject_template_creates_from_default(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        """Test get_pyproject_template creates template from default when none exists."""
        # Create a fresh config instance for this test
        cfg_dir = tmp_path / "config"
        cfg_dir.mkdir()
        dirlock_path = cfg_dir / ".dirlock"
        dirlock_path.write_text("author=HH")

        # Create config file
        config_file = cfg_dir / "config.ini"
        config_file.write_text("[Project]\nproject-name = test")

        mocker.patch(
            "new_python_github_project.config.platformdirs.user_config_dir",
            return_value=str(cfg_dir),
        )

        config = Config()

        # Mock importlib.resources for default template
        mock_files = mocker.patch("importlib.resources.files")
        mock_default_path = mocker.MagicMock()
        mock_files.return_value.joinpath.return_value = mock_default_path
        mock_default_path.exists.return_value = True

        default_content = "default template content"

        # Create the template in the actual filesystem to test the functionality
        templates_dir = config.config_dir / "templates"
        templates_dir.mkdir()
        default_template_path = templates_dir / "pyproject.toml"

        # Create a more realistic mock that only affects the default template reading
        original_open = open

        def selective_mock_open(filename, *args, **kwargs):
            if str(filename) == str(mock_default_path):
                return mock_open(read_data=default_content)()
            return original_open(filename, *args, **kwargs)

        with patch("builtins.open", side_effect=selective_mock_open):
            result = config.get_pyproject_template()

        # Verify the template was created in user config dir
        assert templates_dir.exists()
        assert default_template_path.exists()
        assert result == default_content

    def test_get_pyproject_template_no_default_template(
        self, clean_config_fixture: Config, mocker: MockerFixture
    ) -> None:
        """Test get_pyproject_template raises exception when no default template exists."""
        config = clean_config_fixture

        # Mock importlib.resources for missing default template
        mock_files = mocker.patch("importlib.resources.files")
        mock_default_path = mocker.MagicMock()
        mock_files.return_value.joinpath.return_value = mock_default_path
        mock_default_path.exists.return_value = False

        with pytest.raises(ConfigException, match="No default template found"):
            config.get_pyproject_template()

    def test_read_config_existing_file(self, clean_config_fixture: Config) -> None:
        """Test read_config with existing config file."""
        config = clean_config_fixture
        assert hasattr(config, "config")
        assert isinstance(config.config, configparser.ConfigParser)

    def test_read_config_existing_non_file(self, clean_config_fixture: Config) -> None:
        """Test read_config when config path exists but is not a file."""
        config = clean_config_fixture

        # Replace config file with directory
        config.config_path.unlink(missing_ok=True)
        config.config_path.mkdir()

        with pytest.raises(ConfigException, match="filetype is not file"):
            config.read_config()

    def test_read_config_creates_default_when_missing(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        """Test read_config creates default config when file is missing."""
        config = Config.__new__(Config)
        config.config_dir = tmp_path
        config.config_path = tmp_path / "config.ini"

        # Mock copy_default_config and read_defaults
        mock_copy_default = mocker.patch.object(config, "copy_default_config")
        mock_read_defaults = mocker.patch.object(config, "read_defaults")

        # Mock configparser.ConfigParser
        mock_config_parser = mocker.patch("configparser.ConfigParser")
        mock_parser_instance = mocker.MagicMock()
        mock_config_parser.return_value = mock_parser_instance

        config.read_config()

        mock_copy_default.assert_called_once_with(config.config_path)
        mock_read_defaults.assert_called_once_with(mock_parser_instance)
        mock_parser_instance.read.assert_called_once_with(str(config.config_path))

    def test_read_defaults(self, mocker: MockerFixture) -> None:
        """Test read_defaults loads default configuration."""
        config = Config.__new__(Config)

        mock_files = mocker.patch("importlib.resources.files")
        mock_default_path = mocker.MagicMock()
        mock_files.return_value.joinpath.return_value = mock_default_path

        mock_config_parser = mocker.MagicMock()

        config.read_defaults(mock_config_parser)

        mock_files.assert_called_once_with("new_python_github_project.data")
        mock_files.return_value.joinpath.assert_called_once_with("default_config.ini")
        mock_config_parser.read.assert_called_once_with(str(mock_default_path))

    def test_remove_lockfile(self, clean_config_fixture: Config) -> None:
        """Test remove_lockfile removes the lockfile."""
        config = clean_config_fixture
        lockfile_path = config.get_lockfile_path()

        # Create a lockfile
        lockfile_path.write_text("12345")
        assert lockfile_path.exists()

        config.remove_lockfile()
        assert not lockfile_path.exists()

    def test_remove_lockfile_missing_ok(self, clean_config_fixture: Config) -> None:
        """Test remove_lockfile doesn't fail when lockfile doesn't exist."""
        config = clean_config_fixture
        lockfile_path = config.get_lockfile_path()

        # Ensure lockfile doesn't exist
        lockfile_path.unlink(missing_ok=True)
        assert not lockfile_path.exists()

        # Should not raise exception
        config.remove_lockfile()

    def test_write_lockfile(
        self, clean_config_fixture: Config, mocker: MockerFixture
    ) -> None:
        """Test write_lockfile writes current PID to lockfile."""
        config = clean_config_fixture
        lockfile_path = config.get_lockfile_path()

        # Mock os.getpid
        mock_getpid = mocker.patch("os.getpid", return_value=12345)

        config.write_lockfile()

        assert lockfile_path.exists()
        assert lockfile_path.read_text() == "12345"
        mock_getpid.assert_called_once()

    def test_configparser_custom_converter(self, clean_config_fixture: Config) -> None:
        """Test that ConfigParser is created with custom list converter."""
        config = clean_config_fixture

        # The configparser should have the custom list converter
        assert hasattr(config.config, "getlist")

        # Test the converter works (if we can add a test section)
        test_section = "TEST"
        if not config.config.has_section(test_section):
            config.config.add_section(test_section)
        config.config.set(test_section, "test_list", "item1, item2 , item3")

        result = config.config.getlist(test_section, "test_list")
        assert result == ["item1", "item2", "item3"]
