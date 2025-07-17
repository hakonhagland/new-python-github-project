import subprocess
import logging
import sys

def check_deps() -> None:
    """Check that the runtime dependencies are installed."""
    check_uv_installed()

def check_uv_installed() -> None:
    """Check if uv is installed on the system.
    
    NOTE: uv must be installed outside the virtual environment to ensure its own
    dependencies are not accidentally upgraded or uninstalled.
    """
    dep = "uv"
    try:
        subprocess.run(
            ["uv", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        logging.error(f"Missing runtime dependency: {dep}. Please install it first")
        sys.exit(1)


