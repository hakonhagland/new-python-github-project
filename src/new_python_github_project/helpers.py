import os
import sys
import platform
import subprocess
import logging
from new_python_github_project.config import Config
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QIcon


def add_app_to_tray(app: QApplication) -> None:
    """Add the application to the system tray."""

    tray_icon = QSystemTrayIcon(QIcon.fromTheme("applications-python"), parent=app)
    tray_menu = QMenu()
    show_action = tray_menu.addAction("Show")
    quit_action = tray_menu.addAction("Quit")
    tray_icon.setContextMenu(tray_menu)
    tray_icon.setToolTip("Python Project Creator")
    tray_icon.show()
    def on_quit():
        config.remove_lockfile()
        app.quit()
    quit_action.triggered.connect(on_quit)

    def on_show():
        # Placeholder: bring main window to front if implemented
        pass
    show_action.triggered.connect(on_show)


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
                    logging.error(f"Another instance of the application is already running. Exiting.")
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
    app.setStyle('Fusion')
    app.setQuitOnLastWindowClosed(False)
    add_app_to_tray(app)
    app.aboutToQuit.connect(config.remove_lockfile)
    return app


# Since this is a GUI application, it is appropriate to detach it from the terminal. This enables the
# user to close the terminal without killing the application.
# TODO: Check if there is a PyPI module that does this.
def daemonize(config: Config) -> None:
    """Detach the process from the terminal and run in the background.
    
    This function:
    1. Forks a child process
    2. Creates a new session
    3. Redirects standard I/O to /dev/null
    4. Changes working directory to root
    """
    # Fork the first time
    try:
        pid = os.fork()
        if pid > 0:
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


def detach_from_terminal(config: Config) -> None:
    """Detach the process from the terminal if not already detached."""
    if os.getpgrp() == os.tcgetpgrp(sys.stdout.fileno()):
        daemonize(config)
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

