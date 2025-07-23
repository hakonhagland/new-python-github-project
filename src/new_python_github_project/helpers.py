import importlib.resources as resources
import json
import logging
import os
from pathlib import Path
import platform
import sys
import sysconfig
import subprocess

import click
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QGuiApplication

from new_python_github_project.config import Config
from new_python_github_project.exceptions import ConfigException


def check_another_instance_running(config: Config) -> None:
    """Check if another instance of the application is running.

    We do not want two or more instances of the application running at the same time, since
    this could mess up log files and other files.
    This function checks if another instance is running by checking the lockfile.
    If the lockfile exists, it checks if the process is running by trying to send a signal to the process.
    If the process is running, it exits the application.
    """
    lockfile = config.get_lockfile_path()
    if lockfile.exists():
        try:
            with open(lockfile, "r") as f:
                pid = int(f.read().strip())
            # Check if process is running
            if pid > 0:
                try:
                    os.kill(pid, 0)
                    logging.error(
                        "Another instance of the application is already running. Exiting."
                    )
                    sys.exit(1)
                except OSError:
                    logging.error(f"Process {pid} is not running. Removing lockfile.")
                    config.remove_lockfile()
                    return
        except Exception:
            logging.error(f"Error reading lockfile {lockfile}. Removing lockfile.")
            config.remove_lockfile()
            return


def create_qapplication(config: Config) -> QApplication:
    """Create a new QApplication instance."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setQuitOnLastWindowClosed(False)
    _load_icons(app, config)

    # Set application display name
    app.setApplicationDisplayName("New Python GitHub Project")
    app.setApplicationName("New Python GitHub Project")
    
    # Set application metadata for better desktop integration
    app.setOrganizationName("hakonhagland")
    app.setOrganizationDomain("github.com")
    app.setApplicationVersion("1.0.0")

    # TODO: The app does not need a tray icon yet, but it is possible to add it back later
    #  _add_app_to_tray(app, config)
    app.aboutToQuit.connect(config.remove_lockfile)
    return app


# Since this is a GUI application, it is appropriate to detach it from the terminal. This enables the
# user to close the terminal without killing the application.
# TODO: Check if there is a PyPI module that does this.
def daemonize(config: Config, verbose: bool = False) -> None:
    """Detach the process from the terminal and run in the background.

    This function:
    1. Forks a child process
    2. Creates a new session
    3. Redirects standard I/O to /dev/null
    4. Changes working directory to root
    5. Reconfigures logging for the daemon process

    :param config: Configuration object
    :type config: Config
    :param verbose: Whether to use verbose logging in daemon
    :type verbose: bool
    """
    # Fork the first time
    try:
        pid = os.fork()
        if pid > 0:
            logging.info(
                f"Fork #1 successful. Forked child process with PID {pid}. Parent process exiting."
            )
            # Parent process exits
            os._exit(0)
    except OSError as e:
        logging.error(f"Fork #1 failed: {e}")
        sys.exit(1)

    # Decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)

    # Fork a second time
    try:
        pid = os.fork()
        if pid > 0:
            logging.info("Fork #2 successful. Parent process exiting.")
            # Parent process exits
            os._exit(0)
    except OSError as e:
        logging.error(f"Fork #2 failed: {e}")
        sys.exit(1)

    # Redirect standard file descriptors
    sys.stdout.flush()
    sys.stderr.flush()
    log_path = config.get_logfile_path()
    with open("/dev/null", "r") as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(log_path, "a+") as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())

    # Reconfigure logging for the daemon process
    _setup_daemon_logging(str(log_path), verbose)


def detach_from_terminal(config: Config, ctx: click.Context) -> None:
    """Detach the process from the terminal if not already detached.

    :param config: Configuration object
    :type config: Config
    :param ctx: Click context
    :type ctx: click.Context
    """
    if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
        verbose = ctx.obj.get("VERBOSE", False)
        daemonize(config, verbose)
    config.write_lockfile()


def edit_config_file(config: Config) -> None:
    """Edit the config file.

    This function opens the config file in the user's preferred editor.
    """
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
        logging.error(
            f"Editor not found: {editor}. Please install it first or edit "
            f"the config file {config_path} manually and select another editor"
        )


def debug_to_file(
    message: str, data: dict[str, str] | None = None, debug_file: str = "/tmp/pyqt_debug.log"
) -> None:
    """Write debug information to a file for daemon debugging.

    This is the recommended way to debug daemonized applications since
    breakpoint() doesn't work without an interactive terminal.

    :param message: Debug message
    :type message: str
    :param data: Optional data to log as JSON
    :type data: dict
    :param debug_file: Path to debug log file
    :type debug_file: str
    """
    import datetime

    timestamp = datetime.datetime.now().isoformat()

    debug_info = {
        "timestamp": timestamp,
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "message": message,
    }

    if data:
        debug_info["data"] = data

    try:
        with open(debug_file, "a") as f:
            f.write(json.dumps(debug_info) + "\n")
    except Exception as e:
        # Fallback to stderr if file writing fails
        print(f"DEBUG ERROR: {e}", file=sys.stderr)


def setup_remote_debugging(host: str = "localhost", port: int = 5678) -> None:
    """Setup remote debugging with debugpy.

    This allows you to connect a debugger (like VS Code) to the daemonized process.
    Call this function before daemonizing.

    :param host: Host to bind debug server to
    :type host: str
    :param port: Port for debug server
    :type port: int
    """
    try:
        import debugpy

        debugpy.listen((host, port))
        debug_to_file(f"Remote debugging enabled on {host}:{port}")
        print(f"Remote debugging enabled on {host}:{port}")
        print("Connect your debugger to this address")
    except ImportError:
        debug_to_file("debugpy not installed. Install with: pip install debugpy")
        print("debugpy not installed. Install with: pip install debugpy")


# -----------------------------------------------------
# Private functions
# -----------------------------------------------------


def _add_app_to_tray(app: QApplication, config: Config) -> None:
    """Add the application to the system tray."""

    # Use custom icon for tray if available, fallback to theme icon
    icon_dir = os.path.join(os.path.dirname(__file__), "data")
    icon_256_path = os.path.join(icon_dir, "icon-256.png")
    icon_128_path = os.path.join(icon_dir, "icon-128.png")
    png_icon_path = os.path.join(icon_dir, "icon.png")
    svg_icon_path = os.path.join(icon_dir, "icon.svg")
    
    if os.path.exists(icon_256_path):
        tray_icon = QSystemTrayIcon(QIcon(icon_256_path), parent=app)
    elif os.path.exists(icon_128_path):
        tray_icon = QSystemTrayIcon(QIcon(icon_128_path), parent=app)
    elif os.path.exists(png_icon_path):
        tray_icon = QSystemTrayIcon(QIcon(png_icon_path), parent=app)
    elif os.path.exists(svg_icon_path):
        tray_icon = QSystemTrayIcon(QIcon(svg_icon_path), parent=app)
    else:
        tray_icon = QSystemTrayIcon(QIcon.fromTheme("applications-python"), parent=app)
    
    tray_menu = QMenu()
    show_action = tray_menu.addAction("Show")
    quit_action = tray_menu.addAction("Quit")
    tray_icon.setContextMenu(tray_menu)
    tray_icon.setToolTip("Python Project Creator")
    tray_icon.show()

    def on_quit() -> None:
        config.remove_lockfile()
        app.quit()

    if quit_action is not None:
        quit_action.triggered.connect(on_quit)

    def on_show() -> None:
        # Placeholder: bring main window to front if implemented
        pass

    if show_action is not None:
        show_action.triggered.connect(on_show)

def _load_icons(app: QApplication, config: Config) -> None:
    """Load icons for the application."""
    if platform.system() == "Linux":
        # This is required on Linux to make the app's icon appear in the application menu and dock
        QGuiApplication.setDesktopFileName(config.appname)
    else:
        # On other platforms, we use the hicolor theme
        QIcon.setThemeName("hicolor")
        QIcon.setFallbackThemeName("hicolor")  # fallback if theme not found
        icons_root = _locate_hicolor_icons()
        if icons_root is None:
            logging.warning("Could not locate hicolor icons. Using fallback icon.")
            icon = QIcon.fromTheme("applications-python")
        else:
            QIcon.setThemeSearchPaths([str(icons_root)])  # pyright: ignore
            icon = QIcon.fromTheme(config.appname)
            if icon.isNull():
                icon = QIcon.fromTheme("applications-python")
        app.setWindowIcon(icon)

def _locate_hicolor_icons() -> Path | None:
    # Where pip placed the shared‑data files
    data_root = Path(sysconfig.get_paths()["data"]) / "share" / "icons" / "hicolor"
    if data_root.is_dir():
        return data_root
    # NOTE: If the user did not install the application with "pip install --user", the icons
    #  will not be correctly installed in $XDG_DATA_DIRS/icons/hicolor on Linux.
    return None

def _setup_daemon_logging(log_path: str, verbose: bool = False) -> None:
    """Setup logging for the daemon process after forking.

    This reconfigures the logging module to write to the log file
    instead of the original terminal handlers.

    :param log_path: Path to the log file
    :type log_path: str
    :param verbose: Whether to use verbose logging
    :type verbose: bool
    """
    # Remove all existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create new file handler
    file_handler = logging.FileHandler(log_path, mode="a")

    # Set format similar to basicConfig
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add handler to root logger
    root_logger.addHandler(file_handler)

    # Set log level based on verbose flag
    if verbose:
        root_logger.setLevel(logging.INFO)
    else:
        root_logger.setLevel(logging.WARNING)

    # Log that we've switched to daemon logging
    logging.info("Daemon logging initialized")
