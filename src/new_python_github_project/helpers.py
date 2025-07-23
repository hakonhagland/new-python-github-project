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

if platform.system() == "Windows":
    import ctypes
    from ctypes import wintypes  # noqa: F401


def _is_attached_to_console() -> bool:
    """Check if the current Windows process is attached to a console.

    Returns True if the process is attached to a console (e.g., launched from
    Command Prompt or PowerShell), False otherwise.

    :return: True if attached to console, False otherwise
    :rtype: bool
    """
    if platform.system() != "Windows":
        return False

    try:
        # Try to get console window handle
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        console_window = kernel32.GetConsoleWindow()
        return console_window != 0
    except Exception:
        return False


def _detach_from_console_windows(config: Config, ctx: click.Context) -> None:
    """Detach from console on Windows by restarting the process.

    This function creates a new detached process and exits the current one,
    allowing the terminal prompt to return to the user.

    :param config: Configuration object
    :type config: Config
    :param ctx: Click context
    :type ctx: click.Context
    """
    # Prepare the command to restart the process
    python_exe = sys.executable
    script_args = sys.argv[:]

    # Use the same working directory
    cwd = os.getcwd()

    # Prepare subprocess flags for detachment
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    DETACHED_PROCESS = 0x00000008
    CREATE_NO_WINDOW = 0x08000000

    startup_info = subprocess.STARTUPINFO()  # type: ignore[attr-defined]
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore[attr-defined]
    startup_info.wShowWindow = subprocess.SW_HIDE  # type: ignore[attr-defined]

    try:
        # Start the detached process
        subprocess.Popen(
            [python_exe] + script_args,
            cwd=cwd,
            creationflags=CREATE_NEW_PROCESS_GROUP
            | DETACHED_PROCESS
            | CREATE_NO_WINDOW,
            startupinfo=startup_info,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )

        logging.info("Successfully detached from console. Original process exiting.")
        # Exit the original process so terminal prompt returns
        sys.exit(0)

    except Exception as e:
        logging.error(f"Failed to detach from console: {e}")
        # Continue running attached if detachment fails


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
    1. Forks a child process (Unix only)
    2. Creates a new session (Unix only)
    3. Redirects standard I/O to /dev/null (Unix only)
    4. Changes working directory to root (Unix only)
    5. Reconfigures logging for the daemon process

    On Windows, this function does minimal setup since Windows doesn't support forking.

    :param config: Configuration object
    :type config: Config
    :param verbose: Whether to use verbose logging in daemon
    :type verbose: bool
    """
    if platform.system() == "Windows":
        # Windows doesn't support forking, so just set up logging
        log_path = config.get_logfile_path()
        _setup_daemon_logging(str(log_path), verbose)
        return

    # Unix-specific daemonization
    # Fork the first time
    try:
        pid = os.fork()  # type: ignore[attr-defined]
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
    os.setsid()  # type: ignore[attr-defined]
    os.umask(0)

    # Fork a second time
    try:
        pid = os.fork()  # type: ignore[attr-defined]
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

    On Windows, this function detaches by restarting the process in a detached state.
    On Unix systems, it uses traditional daemonization with forking.

    :param config: Configuration object
    :type config: Config
    :param ctx: Click context
    :type ctx: click.Context
    """
    if platform.system() == "Windows":
        # Check if we're attached to a console and detach if so
        if _is_attached_to_console():
            _detach_from_console_windows(config, ctx)
            # Note: _detach_from_console_windows() calls sys.exit(0) if successful
            # If we reach here, detachment failed but we continue running
        config.write_lockfile()
        return

    # Unix-specific terminal detachment check
    if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):  # type: ignore[attr-defined]
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
    message: str,
    data: dict[str, str] | None = None,
    debug_file: str = "/tmp/pyqt_debug.log",
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
