import json
import logging
import os
import platform
import subprocess
import sys
import sysconfig
from pathlib import Path

import click
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtWidgets import QApplication

from new_python_github_project.config import Config
from new_python_github_project.constants import Directories, FileNames
from new_python_github_project.exceptions import ConfigException

if platform.system() == "Windows":  # pragma: no cover
    # Windows-specific imports - excluded from coverage as they're platform-dependent
    import ctypes  # pragma: no cover
    from ctypes import wintypes  # noqa: F401  # pragma: no cover


# Public functions


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

    # macOS-specific: Fix menu bar application name showing as "Python"
    if platform.system() == "Darwin":  # pragma: no cover
        _fix_macos_app_name()  # pragma: no cover

    app.aboutToQuit.connect(config.remove_lockfile)
    return app


def daemonize(config: Config, verbose: bool = False) -> None:
    """Detach the process from the terminal and run in the background.

    **IMPORTANT**: This function should only be used on Linux/Unix systems where
    GUI frameworks are fork-safe. It should NOT be used on macOS for GUI applications
    due to AppKit/window server limitations. See _detach_macos_gui() for the macOS
    alternative.

    This function implements traditional Unix double-fork daemonization:
    1. First fork: Creates child process, parent exits
    2. Creates new session with setsid()
    3. Changes working directory to root
    4. Second fork: Prevents acquiring controlling terminal
    5. Redirects standard I/O to /dev/null
    6. Reconfigures logging for the daemon process

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

    # Unix-specific daemonization (Linux/macOS/other Unix systems)
    # Note: The type: ignore comments below are needed for Windows CI where these
    # os functions don't exist, but will be marked as "unused" on Unix systems
    # The following daemonization code is excluded from coverage testing because:
    # 1. It requires actual Unix fork() system calls which are not safely mockable
    # 2. Testing would require subprocess/integration testing rather than unit testing
    # 3. The process control and file descriptor manipulation is OS-dependent
    # Fork the first time
    try:  # pragma: no cover
        pid = os.fork()  # type: ignore[attr-defined]  # pragma: no cover
        if pid > 0:  # pragma: no cover
            logging.info(  # pragma: no cover
                f"Fork #1 successful. Forked child process with PID {pid}. Parent process exiting."
            )
            # Parent process exits
            os._exit(0)  # pragma: no cover
    except OSError as e:  # pragma: no cover
        logging.error(f"Fork #1 failed: {e}")  # pragma: no cover
        sys.exit(1)  # pragma: no cover

    # Decouple from parent environment
    os.chdir("/")  # pragma: no cover
    os.setsid()  # type: ignore[attr-defined]  # pragma: no cover
    os.umask(0)  # pragma: no cover

    # Fork a second time
    try:  # pragma: no cover
        pid = os.fork()  # type: ignore[attr-defined]  # pragma: no cover
        if pid > 0:  # pragma: no cover
            logging.info(
                "Fork #2 successful. Parent process exiting."
            )  # pragma: no cover
            # Parent process exits
            os._exit(0)  # pragma: no cover
    except OSError as e:  # pragma: no cover
        logging.error(f"Fork #2 failed: {e}")  # pragma: no cover
        sys.exit(1)  # pragma: no cover

    # Redirect standard file descriptors
    sys.stdout.flush()  # pragma: no cover
    sys.stderr.flush()  # pragma: no cover
    log_path = config.get_logfile_path()  # pragma: no cover
    with open("/dev/null", "r") as f:  # pragma: no cover
        os.dup2(f.fileno(), sys.stdin.fileno())  # pragma: no cover
    with open(log_path, "a+") as f:  # pragma: no cover
        os.dup2(f.fileno(), sys.stdout.fileno())  # pragma: no cover
        os.dup2(f.fileno(), sys.stderr.fileno())  # pragma: no cover

    # Reconfigure logging for the daemon process
    _setup_daemon_logging(str(log_path), verbose)  # pragma: no cover


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


def detach_from_terminal(config: Config, ctx: click.Context) -> None:
    """Detach the process from the terminal if not already detached.

    This function implements platform-specific strategies for detaching GUI applications
    from the terminal while preserving their ability to display windows:

    **Windows**: Uses process restart with special Windows flags (DETACHED_PROCESS, etc.)
    to create a new process that's not attached to the console. This is necessary because
    Windows doesn't have Unix-style forking.

    **macOS**: Uses subprocess restart because PyQt/GUI applications cannot be forked
    on macOS due to AppKit framework limitations and window server connection issues.
    See _detach_macos_gui() for detailed explanation.

    **Linux/Unix**: Uses traditional double-fork daemonization which works well on
    Linux because the X11 window system and GUI frameworks are fork-safe.

    The goal across all platforms is the same: allow the user's terminal to return
    to the prompt while the GUI application continues running in the background.

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

    if platform.system() == "Darwin":
        # macOS: GUI apps cannot use traditional daemonization as it breaks
        # the connection to the window server. Use subprocess restart approach.
        # This is a macOS-specific limitation of PyQt/AppKit framework interaction.
        _detach_macos_gui(config, ctx)
        config.write_lockfile()
        return

    # Linux/Unix systems: Use traditional double-fork daemonization
    # This works because X11 and most Linux GUI frameworks are fork-safe
    # Note: type: ignore needed for Windows CI, will be "unused" on Unix systems
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
        subprocess.Popen([cmd, *args], env=os.environ.copy(), start_new_session=True)
    except FileNotFoundError as e:
        logging.error(f"{e}")
        logging.error(
            f"Editor not found: {editor}. Please install it first or edit "
            f"the config file {config_path} manually and select another editor"
        )


def locate_hicolor_icons() -> Path | None:
    # Where pip placed the shared‑data files
    data_root = Path(sysconfig.get_paths()["data"]) / "share" / "icons" / "hicolor"
    if data_root.is_dir():
        return data_root
    # NOTE: If the user did not install the application with "pip install --user", the icons
    #  will not be correctly installed in $XDG_DATA_DIRS/icons/hicolor on Linux.
    return None


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


# Private functions


def _detach_from_console_windows(
    config: Config, ctx: click.Context
) -> None:  # pragma: no cover
    """Detach from console on Windows by restarting the process.

    This function creates a new detached process and exits the current one,
    allowing the terminal prompt to return to the user.

    :param config: Configuration object
    :type config: Config
    :param ctx: Click context
    :type ctx: click.Context
    """
    # Windows-specific console detachment - excluded from coverage testing because:
    # 1. Requires Windows-specific subprocess flags and process creation
    # 2. Involves actual process spawning and system exit calls
    # 3. Platform-dependent behavior that requires Windows environment to test properly
    # Prepare the command to restart the process
    # Always use pythonw.exe to avoid console window in detached process
    pythonw_exe = sys.executable.replace(
        "python.exe", "pythonw.exe"
    )  # pragma: no cover
    if Path(pythonw_exe).exists():  # pragma: no cover
        executable = pythonw_exe  # pragma: no cover
        script_args = (  # pragma: no cover
            ["-m", "new_python_github_project.main"] + sys.argv[1:] + ["--no-detach"]
        )
    else:  # pragma: no cover
        # Fallback to regular python if pythonw is not available
        executable = sys.executable  # pragma: no cover
        script_args = (  # pragma: no cover
            ["-m", "new_python_github_project.main"] + sys.argv[1:] + ["--no-detach"]
        )

    # Use the same working directory
    cwd = os.getcwd()  # pragma: no cover

    # Prepare subprocess flags for detachment
    CREATE_NEW_PROCESS_GROUP = 0x00000200  # pragma: no cover
    DETACHED_PROCESS = 0x00000008  # pragma: no cover
    CREATE_NO_WINDOW = 0x08000000  # pragma: no cover

    startup_info = subprocess.STARTUPINFO()  # type: ignore[attr-defined]  # pragma: no cover
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore[attr-defined]  # pragma: no cover
    startup_info.wShowWindow = subprocess.SW_HIDE  # type: ignore[attr-defined]  # pragma: no cover

    try:  # pragma: no cover
        # Log the command being executed for debugging
        command = [executable] + script_args  # pragma: no cover
        logging.info(
            f"Starting detached process: {' '.join(command)}"
        )  # pragma: no cover

        # Create log files for the detached process
        log_dir = (
            Path.home() / "AppData" / "Local" / "new-python-gh-project"
        )  # pragma: no cover
        log_dir.mkdir(parents=True, exist_ok=True)  # pragma: no cover
        stdout_log = log_dir / "detached_stdout.log"  # pragma: no cover
        stderr_log = log_dir / "detached_stderr.log"  # pragma: no cover

        # Start the detached process with logging
        # Pass current environment to preserve virtual environment and PATH
        process = subprocess.Popen(  # pragma: no cover
            command,
            cwd=cwd,
            env=os.environ.copy(),  # Preserve current environment including venv
            creationflags=CREATE_NEW_PROCESS_GROUP
            | DETACHED_PROCESS
            | CREATE_NO_WINDOW,
            startupinfo=startup_info,
            stdout=open(str(stdout_log), "w"),
            stderr=open(str(stderr_log), "w"),
            stdin=subprocess.DEVNULL,
        )

        logging.info(  # pragma: no cover
            f"Successfully detached from console. Process PID: {process.pid}. Original process exiting."
        )
        # Exit the original process so terminal prompt returns
        sys.exit(0)  # pragma: no cover

    except Exception as e:  # pragma: no cover
        logging.error(f"Failed to detach from console: {e}")  # pragma: no cover
        logging.error(
            f"Attempted command: {[executable] + script_args}"
        )  # pragma: no cover
        # Continue running attached if detachment fails


# Since this is a GUI application, it is appropriate to detach it from the terminal. This enables the
# user to close the terminal without killing the application.
# TODO: Check if there is a PyPI module that does this.
def _detach_macos_gui(config: Config, ctx: click.Context) -> None:  # pragma: no cover
    """Detach macOS GUI application from terminal using subprocess restart.

    **Why macOS needs special handling:**

    On macOS, GUI applications (especially PyQt/Qt-based ones) cannot be properly
    forked like traditional Unix processes because:

    1. **Window Server Connection**: The macOS window server maintains connections
       to processes that are broken when forking. The child process loses the
       ability to create windows or display GUI elements.

    2. **AppKit Framework**: macOS's AppKit framework (which Qt uses internally)
       is not fork-safe. Forked processes cannot properly initialize or use
       AppKit services required for GUI functionality.

    3. **Process Environment**: GUI applications on macOS require specific
       environment setup and process attributes that are lost during forking.

    **Solution: Subprocess Restart**

    Instead of forking, we restart the entire application as a new subprocess:
    - The new process has a clean GUI environment
    - Window server connections are properly established
    - AppKit framework initializes correctly
    - The original process exits, returning terminal control to the user

    This approach sacrifices some memory efficiency (full process restart vs fork)
    but ensures GUI functionality works correctly on macOS.

    :param config: Configuration object
    :type config: Config
    :param ctx: Click context
    :type ctx: click.Context
    """
    # macOS-specific GUI detachment - excluded from coverage testing because:
    # 1. Requires macOS-specific process handling and GUI framework considerations
    # 2. Involves actual process spawning and system exit calls
    # 3. Platform-dependent behavior that requires macOS environment to test properly
    # Prepare the command to restart the process without detaching
    script_args = (  # pragma: no cover
        ["-m", "new_python_github_project.main"] + sys.argv[1:] + ["--no-detach"]
    )

    # Use the same working directory and executable
    cwd = os.getcwd()  # pragma: no cover
    executable = sys.executable  # pragma: no cover

    try:  # pragma: no cover
        # Log the command being executed for debugging
        command = [executable] + script_args  # pragma: no cover
        logging.info(  # pragma: no cover
            f"macOS GUI detach: Starting detached process: {' '.join(command)}"
        )

        # Create log files for the detached process
        log_dir = config.config_dir  # pragma: no cover
        log_dir.mkdir(parents=True, exist_ok=True)  # pragma: no cover
        stdout_log = log_dir / "detached_stdout.log"  # pragma: no cover
        stderr_log = log_dir / "detached_stderr.log"  # pragma: no cover

        # Start the detached process with proper macOS GUI environment
        # Pass current environment to preserve virtual environment and PATH
        process = subprocess.Popen(  # pragma: no cover
            command,
            cwd=cwd,
            env=os.environ.copy(),  # Preserve current environment including venv
            stdout=open(str(stdout_log), "w"),
            stderr=open(str(stderr_log), "w"),
            stdin=subprocess.DEVNULL,
            start_new_session=True,  # Detach from terminal
        )

        logging.info(  # pragma: no cover
            f"macOS GUI detach: Successfully started detached process. PID: {process.pid}. Original process exiting."
        )
        # Exit the original process so terminal prompt returns
        sys.exit(0)  # pragma: no cover

    except Exception as e:  # pragma: no cover
        logging.error(f"macOS GUI detach failed: {e}")  # pragma: no cover
        logging.error(f"Attempted command: {command}")  # pragma: no cover
        # Continue running attached if detachment fails


def _fix_macos_app_name() -> None:  # pragma: no cover
    """Fix macOS menu bar showing 'Python' instead of application name.

    On macOS, PyQt applications running through the Python interpreter
    show 'Python' in the menu bar by default. This function uses PyObjC
    to dynamically set the CFBundleName to fix this issue.
    """
    # macOS-specific menu bar name fixing - excluded from coverage testing because:
    # 1. Requires macOS-specific PyObjC framework imports and NSBundle API
    # 2. Platform-dependent behavior that requires macOS environment to test properly
    # 3. Testing would require mocking complex Objective-C framework interactions
    try:  # pragma: no cover
        from Foundation import NSBundle  # pragma: no cover

        bundle = NSBundle.mainBundle()  # pragma: no cover
        if bundle:  # pragma: no cover
            app_name = "New Python GitHub Project"  # pragma: no cover
            app_info = (
                bundle.localizedInfoDictionary() or bundle.infoDictionary()
            )  # pragma: no cover

            # For Python scripts, the info dict exists but may be empty
            # We can still modify it to set CFBundleName
            if app_info is not None:  # pragma: no cover
                app_info["CFBundleName"] = app_name  # pragma: no cover
                logging.info(f"Set macOS app name to: {app_name}")  # pragma: no cover
            else:  # pragma: no cover
                logging.warning("Could not get app info dictionary")  # pragma: no cover
        else:  # pragma: no cover
            logging.warning("Could not get NSBundle.mainBundle()")  # pragma: no cover
    except ImportError:  # pragma: no cover
        logging.warning(
            "PyObjC not available - macOS menu bar will show 'Python'"
        )  # pragma: no cover
        logging.info(
            "To fix this, install PyObjC: pip install pyobjc-framework-Cocoa"
        )  # pragma: no cover
    except Exception as e:  # pragma: no cover
        logging.error(f"Error in _fix_macos_app_name(): {e}")  # pragma: no cover


def _is_attached_to_console() -> bool:  # pragma: no cover
    """Check if the current Windows process is attached to a console.

    Returns True if the process is attached to a console (e.g., launched from
    Command Prompt or PowerShell), False otherwise.

    :return: True if attached to console, False otherwise
    :rtype: bool
    """
    # Windows-specific console detection - excluded from coverage testing because:
    # 1. Requires Windows-specific ctypes and kernel32 API calls
    # 2. Platform-dependent behavior that requires Windows environment to test properly
    # 3. Testing would require mocking complex Windows API interactions
    if platform.system() != "Windows":  # pragma: no cover
        return False  # pragma: no cover

    try:  # pragma: no cover
        # Try to get console window handle
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]  # pragma: no cover
        console_window = kernel32.GetConsoleWindow()  # pragma: no cover
        return bool(console_window != 0)  # pragma: no cover
    except Exception:  # pragma: no cover
        return False  # pragma: no cover


def _load_icons(app: QApplication, config: Config) -> None:
    """Load icons for the application."""
    if platform.system() == "Linux":
        # This is required on Linux to make the app's icon appear in the application menu and dock
        QGuiApplication.setDesktopFileName(config.appname)

    # Windows-specific icon handling for better taskbar and window integration
    if platform.system() == "Windows":  # pragma: no cover
        # Windows-specific icon loading - excluded from coverage testing because:
        # 1. Platform-dependent behavior that requires Windows environment to test properly
        # 2. Involves Windows-specific GUI integration and taskbar handling
        icon = _load_windows_icon()  # pragma: no cover
        app.setWindowIcon(icon)  # pragma: no cover
        logging.info(f"Loaded Windows icon: {icon}")  # pragma: no cover
        return  # pragma: no cover

    # Set up icon theme and load icon for Linux/macOS
    QIcon.setThemeName("hicolor")
    QIcon.setFallbackThemeName("hicolor")  # fallback if theme not found
    icons_root = locate_hicolor_icons()
    if icons_root is None:
        logging.warning("Could not locate hicolor icons. Using fallback icon.")
        icon = QIcon.fromTheme("applications-python")
    else:
        logging.info(f"Setting icon search path to {icons_root}")
        QIcon.setThemeSearchPaths([str(icons_root)])  # pyright: ignore
        icon = QIcon.fromTheme(config.appname)
        if icon.isNull():
            logging.warning("Could not load icon from theme. Using fallback icon.")
            icon = QIcon.fromTheme("applications-python")
        else:
            logging.info(f"Loaded icon from theme: {icon}")

    # Set window icon on all platforms
    app.setWindowIcon(icon)


def _load_windows_icon() -> QIcon:  # pragma: no cover
    """Load icon specifically for Windows platform.

    Uses direct file paths for better Windows taskbar integration.
    Tries multiple icon sizes from the hicolor icon directory with fallback to data directory.

    :returns: QIcon object for Windows
    :rtype: QIcon
    """
    # Windows-specific icon loading - excluded from coverage testing because:
    # 1. Platform-dependent behavior that requires Windows environment to test properly
    # 2. Involves Windows-specific file system paths and GUI integration
    # 3. Testing would require mocking complex file system and Qt icon interactions
    # Use the proper hicolor icons directory location
    hicolor_dir = locate_hicolor_icons()  # pragma: no cover

    if hicolor_dir is None:  # pragma: no cover
        logging.warning(  # pragma: no cover
            "Could not locate hicolor icons directory for Windows. Using theme fallback."
        )
        return QIcon.fromTheme("applications-python")  # pragma: no cover

    # Try hicolor icons in order of preference for Windows
    hicolor_paths = [  # pragma: no cover
        hicolor_dir
        / Directories.icon_512x512
        / Directories.icon_app_dir
        / FileNames.icon_png,  # Best for Windows
        hicolor_dir
        / Directories.icon_256x256
        / Directories.icon_app_dir
        / FileNames.icon_png,  # Good fallback
        hicolor_dir
        / Directories.icon_48x48
        / Directories.icon_app_dir
        / FileNames.icon_png,  # Smaller fallback
    ]

    # Create icon with multiple sizes for best Windows display
    icon = QIcon()  # pragma: no cover
    found_icon = False  # pragma: no cover

    # Try hicolor icons first (proper application icons)
    for icon_path in hicolor_paths:  # pragma: no cover
        if icon_path.exists():  # pragma: no cover
            logging.info(
                f"Loading Windows hicolor icon: {icon_path}"
            )  # pragma: no cover
            icon.addFile(str(icon_path))  # pragma: no cover
            found_icon = True  # pragma: no cover

    if not found_icon:  # pragma: no cover
        logging.warning(
            "No custom icons found for Windows. Using theme fallback."
        )  # pragma: no cover
        icon = QIcon.fromTheme("applications-python")  # pragma: no cover

    return icon  # pragma: no cover


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
