class TaskListFrame(QFrame):
    """Frame containing the task list with scrollable area."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_tasks()
    
    def setup_ui(self):
        """Setup the task list frame."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Tasks")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Scroll area for tasks
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container widget for tasks
        self.tasks_widget = QWidget()
        self.tasks_layout = QVBoxLayout(self.tasks_widget)
        self.tasks_layout.setSpacing(5)
        self.tasks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.tasks_widget)
        layout.addWidget(self.scroll_area)
        
        # Style the frame
        self.setFrameStyle(QFrame.Shape.Box)
    
    def load_sample_tasks(self):
        """Load sample tasks for testing.
        
        TASK ORDERING LOGIC:
        The tasks are ordered in a logical workflow sequence that follows the natural
        progression of setting up a Python project. This ordering is designed to:
        
        1. Start with fundamental project identity (name, directory)
        2. Move to technical foundation choices (Python version, license)
        3. Add project metadata (description, author)
        4. Configure development tools (testing framework, code style)
        5. Finish with deployment/repository settings
        
        This order minimizes cognitive load by grouping related tasks together and
        follows dependencies (e.g., package name comes after project name).
        
        WHEN ADDING NEW TASKS:
        - Consider where the task fits in the logical workflow
        - Place it in the appropriate section below
        - Update the section comments if needed
        - Ensure the task description is unique
        """
        import os
        
        # Get current directory as default for project directory
        current_dir = os.getcwd()
        
        # ============================================================================
        # SECTION 1: PROJECT FUNDAMENTALS (Name, Location)
        # These are the basic identity and location of the project
        # ============================================================================
        project_fundamentals = [
            Task("Set project name", has_default=False),  # Required - no sensible default
            Task("Set project directory", has_default=True, default_value=current_dir),  # Default to current directory
        ]
        
        # ============================================================================
        # SECTION 2: TECHNICAL FOUNDATION (Language, License)
        # These define the technical environment and legal framework
        # ============================================================================
        technical_foundation = [
            Task("Choose Python version", has_default=True, default_value=">=3.8"),  # Default to Python 3.8+
            Task("Choose license", has_default=True, default_value="MIT"),  # Default to MIT
        ]
        
        # ============================================================================
        # SECTION 3: PROJECT METADATA (Description, Author)
        # These provide context and attribution for the project
        # ============================================================================
        project_metadata = [
            Task("Set project description", has_default=False),  # Required - no sensible default
            Task("Set author name", has_default=True, default_value="Håkon Hægland"),  # Default from config file
        ]
        
        # ============================================================================
        # SECTION 4: DEVELOPMENT TOOLS (Testing, Code Style)
        # These configure the development environment and quality tools
        # ============================================================================
        development_tools = [
            Task("Choose testing framework", has_default=True),  # Has sensible default
            Task("Set package name", has_default=False),  # Required - depends on project name
            Task("Choose code style", has_default=True),  # Has sensible default
        ]
        
        # ============================================================================
        # SECTION 5: DEPLOYMENT & REPOSITORY (Repository URL)
        # These are for publishing and sharing the project
        # ============================================================================
        deployment_repository = [
            Task("Set repository URL", has_default=False),  # Optional but common
        ]
        
        # Combine all sections in logical order
        sample_tasks = (
            project_fundamentals +
            technical_foundation +
            project_metadata +
            development_tools +
            deployment_repository
        )
        
        for task in sample_tasks:
            task_widget = TaskItemWidget(task)
            self.tasks_layout.addWidget(task_widget)
        
        # Store reference to all tasks for validation
        self.all_tasks = sample_tasks
    
    def get_incomplete_required_tasks(self):
        """Get list of tasks that require user input but are not completed.
        
        Returns:
            list: List of Task objects that have no default and are not completed
        """
        incomplete_tasks = []
        for task in self.all_tasks:
            # Check if task requires user input (no default) and is not completed
            if not task.has_default and not task.is_completed:
                incomplete_tasks.append(task)
        return incomplete_tasks


class ActionButtonsFrame(QFrame):
    """Frame containing action buttons."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the action buttons frame."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Actions")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Create button
        create_button = QPushButton("Create")
        create_button.setMinimumHeight(30)
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        create_button.clicked.connect(self.on_create_clicked)
        
        button_layout.addWidget(create_button)
        button_layout.addStretch()  # Push button to the left
        
        layout.addLayout(button_layout)
        
        # Style the frame
        self.setFrameStyle(QFrame.Shape.Box)
    
    def on_create_clicked(self):
        """Handle create button click."""
        # Get the main window
        main_window = self.window()
        
        # Get the task list frame to access tasks
        task_list_frame = main_window.task_list
        
        # Check for incomplete required tasks
        incomplete_tasks = task_list_frame.get_incomplete_required_tasks()
        
        if incomplete_tasks:
            # Show error dialog with list of incomplete tasks
            self.show_incomplete_tasks_dialog(incomplete_tasks)
        else:
            # All required tasks are completed, proceed with project creation
            if hasattr(main_window, 'add_log_message'):
                main_window.add_log_message("✓ All tasks completed! Project structure creation would proceed here.")
                main_window.add_log_message("📁 Creating project structure...")
                main_window.add_log_message("📄 Generating configuration files...")
                main_window.add_log_message("✅ Project setup complete!")
    
    def show_incomplete_tasks_dialog(self, incomplete_tasks):
        """Show error dialog listing incomplete required tasks."""
        # Build the message
        message = "The following tasks require your input before creating the project:\n\n"
        
        for task in incomplete_tasks:
            message += f"• {task.description}\n"
        
        message += "\nPlease complete these tasks and try again."
        
        # Show error dialog
        QMessageBox.critical(
            self,
            "Incomplete Tasks",
            message,
            QMessageBox.StandardButton.Ok
        )


class TerminalFrame(QFrame):
    """Frame containing the terminal-like output area."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_sample_output()
    
    def setup_ui(self):
        """Setup the terminal frame."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Title
        title = QLabel("Terminal Output")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #333; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Terminal text area
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Monospace", 10))
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        # Set line wrap mode to wrap at word boundaries
        self.terminal.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        layout.addWidget(self.terminal)
        
        # Style the frame
        self.setFrameStyle(QFrame.Shape.Box)
    
    def load_sample_output(self):
        """Load sample terminal output."""
        sample_messages = [
            "Application started successfully",
            "Loading configuration...",
            "Configuration loaded successfully",
            "Initializing UI components...",
            "UI components initialized",
            "Ready for user interaction",
            "This is a very long log message that demonstrates how the terminal handles long lines that need to be wrapped at the right edge of the window without horizontal scrollbars",
            "Another message with reasonable length",
            "System status: OK",
            "All services running normally"
        ]
        
        for message in sample_messages:
            self.add_log_message(message)
    
    def add_log_message(self, message):
        """Add a log message to the terminal."""
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.terminal.setTextCursor(cursor)
        
        # Add timestamp and message
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.terminal.insertPlainText(formatted_message)
        
        # Auto-scroll to bottom
        self.terminal.ensureCursorVisible()


class MainWindow(QMainWindow):
    """Main application window with three vertical areas."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle("PyQt6 UI Testing - Three Area Layout")
        
        # Set default window size
        default_width = 1250
        default_height = 970
        
        # Get screen size and adjust window size if needed
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        
        # Adjust window size if it's too large for the screen
        # Leave some margin (50 pixels) to ensure window fits
        max_width = self.screen_width - 50
        max_height = self.screen_height - 50
        
        self.window_width = min(default_width, max_width)
        self.window_height = min(default_height, max_height)
        
        # Center the window on screen
        x = (self.screen_width - self.window_width) // 2
        y = (self.screen_height - self.window_height) // 2
        
        self.setGeometry(x, y, self.window_width, self.window_height)
        
        # Setup menu bar
        self.setup_menu()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Area A1: Task List (42.5% of height)
        self.task_list = TaskListFrame()
        layout.addWidget(self.task_list, 42)
        
        # Area A2: Action Buttons (10% of height)
        self.action_buttons = ActionButtonsFrame()
        layout.addWidget(self.action_buttons, 10)
        
        # Area A3: Terminal Output (42.5% of height)
        self.terminal_frame = TerminalFrame()
        layout.addWidget(self.terminal_frame, 42)
        
        # Store reference to terminal for other components
        self.terminal = self.terminal_frame.terminal
        
        # Log the window size information
        self.add_log_message(f"Screen size: {self.screen_width}x{self.screen_height}")
        self.add_log_message(f"Window size: {self.window_width}x{self.window_height}")
        if self.window_width < default_width or self.window_height < default_height:
            self.add_log_message("Window size adjusted to fit screen")
    
    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.setStatusTip("Quit the application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
    
    def add_log_message(self, message):
        """Add a log message to the terminal."""
        self.terminal_frame.add_log_message(message)
    
    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        width = event.size().width()
        height = event.size().height()
        self.add_log_message(f"Window resized to: {width}x{height} pixels")
