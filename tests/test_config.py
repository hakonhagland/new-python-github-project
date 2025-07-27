import configparser
import typing
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest
from pytest_mock.plugin import MockerFixture

from new_python_github_project.config import Config
from new_python_github_project.constants import Directories, FileNames
from new_python_github_project.exceptions import ConfigException

from .common import GetConfig, PytestDataDict


class TestConfig:
    """Test suite for Config class."""

    def test_class_variables(self) -> None:
        """Test that class variables are correctly set."""
        assert Config.appname == Config.appname
        assert Config.config_fn == Config.config_fn
        assert Config.dirlock_fn == Config.dirlock_fn
        assert Config.lockfile_fn == Config.lockfile_fn
        assert Config.logfile_fn == Config.logfile_fn
        assert Config.dirlock_string == Config.dirlock_string

    def test_init_creates_config_properly(self, get_config: GetConfig) -> None:
        """Test that Config initialization works properly."""
        config = get_config()
        assert isinstance(config, Config)
        assert config.config_dir.exists()
        assert config.config_path.exists()
        assert hasattr(config, "config")

    def test_check_correct_config_dir_valid_lock(self, tmp_path: Path) -> None:
        """Test check_correct_config_dir with valid lock file."""
        config = Config.__new__(Config)  # Create without __init__
        config.dirlock_string = Config.dirlock_string

        lock_file = tmp_path / Config.dirlock_fn
        lock_file.write_text(Config.dirlock_string + "\n")

        # Should not raise exception
        config.check_correct_config_dir(lock_file)

    def test_check_correct_config_dir_bad_content(self, tmp_path: Path) -> None:
        """Test check_correct_config_dir with bad lock file content."""
        config = Config.__new__(Config)
        config.dirlock_string = Config.dirlock_string

        lock_file = tmp_path / Config.dirlock_fn
        lock_file.write_text("bad content")

        with pytest.raises(ConfigException, match="bad content"):
            config.check_correct_config_dir(lock_file)

    def test_check_correct_config_dir_is_directory(self, tmp_path: Path) -> None:
        """Test check_correct_config_dir when lock file is a directory."""
        config = Config.__new__(Config)
        config.dirlock_string = Config.dirlock_string

        lock_file = tmp_path / Config.dirlock_fn
        lock_file.mkdir()

        with pytest.raises(ConfigException, match="is a directory"):
            config.check_correct_config_dir(lock_file)

    def test_check_correct_config_dir_missing(self, tmp_path: Path) -> None:
        """Test check_correct_config_dir when lock file is missing."""
        config = Config.__new__(Config)
        config.dirlock_string = Config.dirlock_string

        lock_file = tmp_path / Config.dirlock_fn

        with pytest.raises(ConfigException, match="missing"):
            config.check_correct_config_dir(lock_file)

    def test_copy_default_config(self, tmp_path: Path, mocker: MockerFixture) -> None:
        """Test copying default config file."""
        config = Config.__new__(Config)
        target_path = tmp_path / Config.config_fn

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
        self, mocker: MockerFixture, tmp_path: Path, test_data: PytestDataDict
    ) -> None:
        """Test get_config_dir with existing valid directory."""
        config = Config.__new__(Config)
        config.appname = "test-app"
        config.dirlock_fn = Config.dirlock_fn
        config.dirlock_string = Config.dirlock_string

        # Create existing directory with valid lock file
        config_dir = tmp_path / test_data["config_dir"]
        config_dir.mkdir()
        lock_file = config_dir / Config.dirlock_fn
        lock_file.write_text(Config.dirlock_string)

        mocker.patch("platformdirs.user_config_dir", return_value=str(config_dir))

        result = config.get_config_dir()
        assert result == config_dir

    def test_get_config_dir_existing_file_not_directory(
        self, mocker: MockerFixture, tmp_path: Path, test_data: PytestDataDict
    ) -> None:
        """Test get_config_dir when path exists but is a file."""
        config = Config.__new__(Config)
        config.appname = "test-app"

        # Create a file instead of directory
        config_path = tmp_path / test_data["config_dir"]
        config_path.write_text("not a directory")

        mocker.patch("platformdirs.user_config_dir", return_value=str(config_path))

        with pytest.raises(ConfigException, match="is file. Expected directory"):
            config.get_config_dir()

    def test_get_config_dir_creates_new_directory(
        self,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test get_config_dir creates new directory when it doesn't exist."""
        config = Config.__new__(Config)
        config.appname = "test-app"
        config.dirlock_fn = Config.dirlock_fn
        config.dirlock_string = Config.dirlock_string

        config_dir = tmp_path / "new_config"

        mocker.patch("platformdirs.user_config_dir", return_value=str(config_dir))

        result = config.get_config_dir()

        assert result == config_dir
        assert config_dir.exists()
        assert config_dir.is_dir()

        lock_file = config_dir / Config.dirlock_fn
        assert lock_file.exists()
        assert lock_file.read_text() == Config.dirlock_string

    def test_get_config_file(self, get_config: GetConfig) -> None:
        """Test get_config_file returns correct path."""
        config = get_config()
        config_file = config.get_config_file()
        assert config_file == config.config_path
        assert config_file.name == Config.config_fn

    def test_get_lockfile_path(self, get_config: GetConfig) -> None:
        """Test get_lockfile_path returns correct path."""
        config = get_config()
        lockfile_path = config.get_lockfile_path()
        expected_path = config.config_dir / Config.lockfile_fn
        assert lockfile_path == expected_path

    def test_get_logfile_path(self, get_config: GetConfig) -> None:
        """Test get_logfile_path returns correct path."""
        config = get_config()
        logfile_path = config.get_logfile_path()
        expected_path = config.config_dir / Config.logfile_fn
        assert logfile_path == expected_path

    def test_get_pyproject_template_existing_template(
        self, get_config: GetConfig
    ) -> None:
        """Test get_pyproject_template with existing template."""
        config = get_config()

        # Create templates directory and template file
        templates_dir = config.config_dir / Directories.templates
        templates_dir.mkdir(exist_ok=True)
        template_file = templates_dir / FileNames.pyproject_toml
        template_content = (
            "name = %%PROJECT_NAME%%\ndescription = %%PROJECT_DESCRIPTION%%"
        )
        template_file.write_text(template_content)

        result = config.get_pyproject_template()
        assert result == template_content

    def test_get_pyproject_template_creates_from_default(
        self, tmp_path: Path, mocker: MockerFixture, test_data: PytestDataDict
    ) -> None:
        """Test get_pyproject_template creates template from default when none exists."""
        # Create a fresh config instance for this test
        cfg_dir = tmp_path / test_data["config_dir"]
        cfg_dir.mkdir()
        dirlock_path = cfg_dir / Config.dirlock_fn
        dirlock_path.write_text(Config.dirlock_string)

        # Create config file
        config_file = cfg_dir / Config.config_fn
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
        templates_dir = config.config_dir / Directories.templates
        templates_dir.mkdir()
        default_template_path = templates_dir / FileNames.pyproject_toml

        # Create a more realistic mock that only affects the default template reading
        original_open = open

        def selective_mock_open(
            filename: str, *args: typing.Any, **kwargs: typing.Any
        ) -> typing.Any:
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
        self, get_config: GetConfig, mocker: MockerFixture
    ) -> None:
        """Test get_pyproject_template raises exception when no default template exists."""
        config = get_config()

        # Mock importlib.resources for missing default template
        mock_files = mocker.patch("importlib.resources.files")
        mock_default_path = mocker.MagicMock()
        mock_files.return_value.joinpath.return_value = mock_default_path
        mock_default_path.exists.return_value = False

        with pytest.raises(ConfigException, match="No default template found"):
            config.get_pyproject_template()

    def test_read_config_existing_file(self, get_config: GetConfig) -> None:
        """Test read_config with existing config file."""
        config = get_config()
        assert hasattr(config, "config")
        assert isinstance(config.config, configparser.ConfigParser)

    def test_read_config_existing_non_file(self, get_config: GetConfig) -> None:
        """Test read_config when config path exists but is not a file."""
        config = get_config()

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
        config.config_path = tmp_path / Config.config_fn

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

    def test_remove_lockfile(self, get_config: GetConfig) -> None:
        """Test remove_lockfile removes the lockfile."""
        config = get_config()
        lockfile_path = config.get_lockfile_path()

        # Create a lockfile
        lockfile_path.write_text("12345")
        assert lockfile_path.exists()

        config.remove_lockfile()
        assert not lockfile_path.exists()

    def test_remove_lockfile_missing_ok(self, get_config: GetConfig) -> None:
        """Test remove_lockfile doesn't fail when lockfile doesn't exist."""
        config = get_config()
        lockfile_path = config.get_lockfile_path()

        # Ensure lockfile doesn't exist
        lockfile_path.unlink(missing_ok=True)
        assert not lockfile_path.exists()

        # Should not raise exception
        config.remove_lockfile()

    def test_write_lockfile(self, get_config: GetConfig, mocker: MockerFixture) -> None:
        """Test write_lockfile writes current PID to lockfile."""
        config = get_config()
        lockfile_path = config.get_lockfile_path()

        # Mock os.getpid
        mock_getpid = mocker.patch("os.getpid", return_value=12345)

        config.write_lockfile()

        assert lockfile_path.exists()
        assert lockfile_path.read_text() == "12345"
        mock_getpid.assert_called_once()

    def test_configparser_custom_converter(self, get_config: GetConfig) -> None:
        """Test that ConfigParser is created with custom list converter."""
        config = get_config()

        # The configparser should have the custom list converter
        assert hasattr(config.config, "getlist")

        # Test the converter works (if we can add a test section)
        test_section = "TEST"
        if not config.config.has_section(test_section):
            config.config.add_section(test_section)
        config.config.set(test_section, "test_list", "item1, item2 , item3")

        result = config.config.getlist(test_section, "test_list")
        assert result == ["item1", "item2", "item3"]

    def test_get_method_delegation(self, get_config: GetConfig) -> None:
        """Test that get() method properly delegates to ConfigParser.get()."""
        config = get_config()

        # Add a test section and value
        test_section = "TEST"
        if not config.config.has_section(test_section):
            config.config.add_section(test_section)
        config.config.set(test_section, "test_option", "test_value")

        # Test the delegation method
        result = config.get(test_section, "test_option")
        assert result == "test_value"

        # Test with additional kwargs
        result_with_fallback = config.get(
            test_section, "nonexistent", fallback="default"
        )
        assert result_with_fallback == "default"

    def test_getboolean_method_delegation(self, get_config: GetConfig) -> None:
        """Test that getboolean() method properly delegates to ConfigParser.getboolean()."""
        config = get_config()

        # Add a test section and boolean values
        test_section = "TEST"
        if not config.config.has_section(test_section):
            config.config.add_section(test_section)
        config.config.set(test_section, "bool_true", "true")
        config.config.set(test_section, "bool_false", "false")

        # Test the delegation method
        result_true = config.getboolean(test_section, "bool_true")
        assert result_true is True

        result_false = config.getboolean(test_section, "bool_false")
        assert result_false is False

        # Test with additional kwargs
        result_with_fallback = config.getboolean(
            test_section, "nonexistent", fallback=True
        )
        assert result_with_fallback is True

    def test_getfloat_method_delegation(self, get_config: GetConfig) -> None:
        """Test that getfloat() method properly delegates to ConfigParser.getfloat()."""
        config = get_config()

        # Add a test section and float values
        test_section = "TEST"
        if not config.config.has_section(test_section):
            config.config.add_section(test_section)
        config.config.set(test_section, "float_value", "3.14")
        config.config.set(test_section, "int_as_float", "42")

        # Test the delegation method
        result_float = config.getfloat(test_section, "float_value")
        assert result_float == 3.14

        result_int = config.getfloat(test_section, "int_as_float")
        assert result_int == 42.0

        # Test with additional kwargs
        result_with_fallback = config.getfloat(
            test_section, "nonexistent", fallback=1.5
        )
        assert result_with_fallback == 1.5

    def test_getint_method_delegation(self, get_config: GetConfig) -> None:
        """Test that getint() method properly delegates to ConfigParser.getint()."""
        config = get_config()

        # Add a test section and integer values
        test_section = "TEST"
        if not config.config.has_section(test_section):
            config.config.add_section(test_section)
        config.config.set(test_section, "int_value", "42")
        config.config.set(test_section, "float_as_int", "3")

        # Test the delegation method
        result_int = config.getint(test_section, "int_value")
        assert result_int == 42

        result_float = config.getint(test_section, "float_as_int")
        assert result_float == 3

        # Test with additional kwargs
        result_with_fallback = config.getint(test_section, "nonexistent", fallback=99)
        assert result_with_fallback == 99
