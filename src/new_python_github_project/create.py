from pathlib import Path
from new_python_github_project.config import Config

class ProjectCreator():
    """Create a new Python project on GitHub."""

    def __init__(self, config: Config, project_name: str) -> None:
        self.config = config
        self.project_name = project_name
        self.project_dir = Path(project_name.replace("-", "_")).resolve()
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self._create_project_structure()
        self._create_pyproject_toml()
        self._create_readme()

    def _create_project_structure(self) -> None:
        """Create the project structure."""
        # Create the project directory
        (self.project_dir / "src").mkdir(parents=True, exist_ok=True)
        (self.project_dir / "tests").mkdir(parents=True, exist_ok=True)

    def _create_pyproject_toml(self) -> None:
        """Create the pyproject.toml file."""
        # Create the pyproject.toml file
        # Get dependency versions from config
        template = self.config.get_pyproject_template()
        deps = self.config.config["Dependencies"]
        python_version = deps["python-version"]

    def _create_readme(self) -> None:
        """Create the README.md file."""
        # Create the README.md file
        (self.project_dir / "README.md").write_text(self.config.get_readme())


