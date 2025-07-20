from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QTextEdit,
    QDialog,
    QLineEdit,
    QDialogButtonBox,
    QFileDialog,
    QComboBox,
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont


class Task:
    """Represents a task with status information."""

    def __init__(
        self, description, has_default=False, is_completed=False, default_value=None
    ):
        self.description = description
        self.has_default = has_default
        self.is_completed = is_completed
        self.default_value = default_value
        self.user_modified = False  # Track if user has modified the default
        self.configured_value = None  # Store the value configured by the user
        self.configured_values = {}  # Store multiple values for multi-parameter tasks

    @property
    def status(self):
        """Returns the status of the task."""
        if self.is_completed or self.has_default:
            return "completed"  # Green checkmark
        else:
            return "pending"  # Red question mark

    def get_tooltip_text(self):
        """Returns the appropriate tooltip text based on task state."""
        if self.status == "pending":
            return "User input required"
        elif self.user_modified:
            return "Completed"
        else:
            return "Use default"

    def _truncate_path(self, value):
        """Helper method to truncate long paths for display."""
        if len(value) > 50:
            # Smart truncation: find the nearest path separator after position 50
            start_pos = 50
            # Look for path separator in the next 20 characters
            search_range = min(20, len(value) - start_pos)
            separator_pos = -1

            for i in range(start_pos, start_pos + search_range):
                if value[i] == "/":  # Unix path separator
                    separator_pos = i
                    break

            if separator_pos != -1:
                # Truncate at the separator (including the separator)
                return "..." + value[separator_pos:]
            else:
                # No separator found, truncate at the original position
                return "..." + value[-50:]
        else:
            return value

    def get_display_text(self):
        """Returns the display text for the task with current state hints."""
        base_text = self.description

        if self.status == "pending":
            # For pending tasks, show [?] or nothing
            return base_text

        # For completed tasks, show the configured value(s)
        if hasattr(self, "configured_value") and self.configured_value:
            # Single value task
            value = self.configured_value
            truncated_value = self._truncate_path(value)
            return f"{base_text} <span style='color: #FF8C00; font-style: italic;'>[{truncated_value}]</span>"
        elif hasattr(self, "configured_values") and self.configured_values:
            # Multi-value task - show count of configured parameters
            param_count = len(self.configured_values)
            return f"{base_text} <span style='color: #FF8C00; font-style: italic;'>[{param_count} params]</span>"
        else:
            # Completed but no specific value stored (e.g., default used)
            if self.has_default and self.default_value:
                truncated_value = self._truncate_path(self.default_value)
                return f"{base_text} <span style='color: #FF8C00; font-style: italic;'>[{truncated_value}]</span>"
            else:
                return f"{base_text} <span style='color: #FF8C00; font-style: italic;'>[✓]</span>"


class TaskItemWidget(QWidget):
    """Widget containing a task with status icon and clickable label."""

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setup_ui()

    def setup_ui(self):
        """Setup the task item widget."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Status icon
        self.status_label = QLabel()
        self.status_label.setFixedSize(28, 28)
        self.update_status_icon()
        layout.addWidget(self.status_label)

        # Task description
        self.task_label = ClickableLabel(self.task.get_display_text())
        layout.addWidget(self.task_label, 1)  # Take remaining space

        # Make the entire widget clickable
        self.setMouseTracking(True)

        # Style the widget with static appearance and tooltip styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 2px;
            }
            QToolTip {
                color: #333;
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
                font-weight: normal;
            }
        """)

    def update_status_icon(self):
        """Update the status icon based on task status."""
        if self.task.status == "completed":
            # Green checkmark (using text for now, could use actual icon)
            self.status_label.setText("✓")
            self.status_label.setStyleSheet(
                "color: #4CAF50; font-weight: bold; font-size: 20px;"
            )
        else:
            # Red question mark
            self.status_label.setText("?")
            self.status_label.setStyleSheet(
                "color: #f44336; font-weight: bold; font-size: 20px;"
            )

        # Remove default tooltip and implement custom tooltip
        self.status_label.setToolTip("")
        self.custom_tooltip = None

        # Install event filter for custom tooltip
        self.status_label.installEventFilter(self)

    def mark_as_completed(self):
        """Mark the task as completed by user modification."""
        self.task.is_completed = True
        self.task.user_modified = True
        self.update_status_icon()
        self.update_task_label()

    def update_task_label(self):
        """Update the task label text to reflect current state."""
        self.task_label.setText(self.task.get_display_text())

    def mark_as_using_default(self):
        """Mark the task as using default value."""
        self.task.is_completed = True
        self.task.user_modified = False
        self.update_status_icon()

    def eventFilter(self, obj, event):
        """Handle custom tooltip events."""
        if obj == self.status_label:
            if event.type() == QEvent.Type.Enter:
                self.show_custom_tooltip(event)
                return True
            elif event.type() == QEvent.Type.Leave:
                self.hide_custom_tooltip()
                return True
        return super().eventFilter(obj, event)

    def show_custom_tooltip(self, event):
        """Show custom tooltip with consistent styling."""
        if self.custom_tooltip is None:
            self.custom_tooltip = QLabel(self.task.get_tooltip_text())
            self.custom_tooltip.setStyleSheet("""
                QLabel {
                    color: #333;
                    background-color: #f8f8f8;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 4px;
                    font-size: 12px;
                    font-weight: normal;
                }
            """)
            self.custom_tooltip.setWindowFlags(Qt.WindowType.ToolTip)

        # Position tooltip near the mouse
        pos = event.globalPosition().toPoint()
        self.custom_tooltip.move(pos.x() + 10, pos.y() + 10)
        self.custom_tooltip.show()

    def hide_custom_tooltip(self):
        """Hide custom tooltip."""
        if self.custom_tooltip:
            self.custom_tooltip.hide()
            self.custom_tooltip = None

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_task_clicked()
        super().mousePressEvent(event)

    def on_task_clicked(self):
        """Handle task click."""
        # Add log message to terminal
        main_window = self.window()  # Get the main window
        if hasattr(main_window, "add_log_message"):
            main_window.add_log_message(f"Task selected: {self.task.description}")

        # Open task configuration dialog
        if self.task.description == "Set project name":
            dialog = TaskConfigDialog(self.task, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                project_name = dialog.get_result()
                # Update the task status and log the result
                self.mark_as_completed()
                # Store the configured value in the task
                self.task.configured_value = project_name
                # Update the label to show the new value
                self.update_task_label()
                main_window = self.window()  # Get the main window
                if hasattr(main_window, "add_log_message"):
                    main_window.add_log_message(
                        f"Project name configured: {project_name}"
                    )
        elif self.task.description == "Set project directory":
            # Open directory selection dialog
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select Project Directory",
                "",  # Start from current directory
                QFileDialog.Option.ShowDirsOnly,
            )

            if directory:
                # Update the task status and log the result
                self.mark_as_completed()
                # Store the configured value in the task
                self.task.configured_value = directory
                # Update the label to show the new value
                self.update_task_label()
                main_window = self.window()  # Get the main window
                if hasattr(main_window, "add_log_message"):
                    main_window.add_log_message(
                        f"Project directory set to: {directory}"
                    )
            else:
                # User cancelled the dialog
                main_window = self.window()  # Get the main window
                if hasattr(main_window, "add_log_message"):
                    main_window.add_log_message("Directory selection cancelled")
        elif self.task.description == "Choose license":
            # Open license selection dialog
            dialog = LicenseSelectionDialog(self.task, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_license = dialog.get_result()
                # Update the task status and log the result
                self.mark_as_completed()
                # Store the configured value in the task
                self.task.configured_value = selected_license
                # Update the label to show the new value
                self.update_task_label()
                main_window = self.window()  # Get the main window
                if hasattr(main_window, "add_log_message"):
                    main_window.add_log_message(f"License selected: {selected_license}")
        elif self.task.description == "Choose Python version":
            # Open Python version selection dialog
            dialog = PythonVersionDialog(self.task, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_version = dialog.get_result()
                # Update the task status and log the result
                self.mark_as_completed()
                # Store the configured value in the task
                self.task.configured_value = selected_version
                # Update the label to show the new value
                self.update_task_label()
                main_window = self.window()  # Get the main window
                if hasattr(main_window, "add_log_message"):
                    main_window.add_log_message(
                        f"Python version configured: {selected_version}"
                    )
        elif self.task.description == "Set project description":
            # Open project description configuration dialog
            dialog = TaskConfigDialog(self.task, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                project_description = dialog.get_result()
                # Update the task status and log the result
                self.mark_as_completed()
                # Store the configured value in the task
                self.task.configured_value = project_description
                # Update the label to show the new value
                self.update_task_label()
                main_window = self.window()  # Get the main window
                if hasattr(main_window, "add_log_message"):
                    main_window.add_log_message(
                        f"Project description configured: {project_description}"
                    )
        elif self.task.description == "Set author name":
            # Open author name configuration dialog
            dialog = TaskConfigDialog(self.task, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                author_name = dialog.get_result()
                # Update the task status and log the result
                self.mark_as_completed()
                # Store the configured value in the task
                self.task.configured_value = author_name
                # Update the label to show the new value
                self.update_task_label()
                main_window = self.window()  # Get the main window
                if hasattr(main_window, "add_log_message"):
                    main_window.add_log_message(
                        f"Author name configured: {author_name}"
                    )
        else:
            main_window = self.window()  # Get the main window
            if hasattr(main_window, "add_log_message"):
                main_window.add_log_message(
                    f"Task '{self.task.description}' - configuration dialog not implemented yet"
                )


class TaskConfigDialog(QDialog):
    """Dialog for configuring task parameters."""

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.result_value = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle(f"Configure: {self.task.description}")
        self.setModal(True)

        # Determine dialog size and input type based on task
        if self.task.description == "Set project description":
            self.setFixedSize(500, 300)  # Larger for descriptions
            self.use_text_edit = True
        else:
            self.setFixedSize(400, 200)  # Standard size for names
            self.use_text_edit = False

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(f"Configure: {self.task.description}")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Input field configuration based on task type
        if self.task.description == "Set project description":
            self.input_label = QLabel("Project description:")
            self.input_field = QTextEdit()  # Multi-line for descriptions
            self.input_field.setPlaceholderText(
                "Enter a brief description of your project..."
            )
            self.input_field.setMaximumHeight(100)

            # Add character count label
            self.char_count_label = QLabel("0 characters")
            self.char_count_label.setStyleSheet("color: #666; font-size: 11px;")
            layout.addWidget(self.input_label)
            layout.addWidget(self.input_field)
            layout.addWidget(self.char_count_label)

            # Connect character count update
            self.input_field.textChanged.connect(self.update_char_count)
        elif self.task.description == "Set author name":
            # Author name input
            self.input_label = QLabel("Author name:")
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText("Enter author name...")
            self.input_field.setMinimumHeight(30)
            layout.addWidget(self.input_label)
            layout.addWidget(self.input_field)
        else:
            # Default for project name and other single-line inputs
            self.input_label = QLabel("Project name:")
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText("Enter project name...")
            self.input_field.setMinimumHeight(30)
            layout.addWidget(self.input_label)
            layout.addWidget(self.input_field)

        # Pre-fill with existing value if available
        if hasattr(self.task, "configured_value") and self.task.configured_value:
            if self.use_text_edit:
                self.input_field.setPlainText(self.task.configured_value)
            else:
                self.input_field.setText(self.task.configured_value)
                # Select all text for easy replacement
                self.input_field.selectAll()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set focus to input field
        self.input_field.setFocus()

        # Connect text changed signal to clear error styling
        if self.use_text_edit:
            self.input_field.textChanged.connect(self.clear_error_styling)
        else:
            self.input_field.textChanged.connect(self.clear_error_styling)

    def update_char_count(self):
        """Update character count for description input."""
        if hasattr(self, "char_count_label"):
            count = len(self.input_field.toPlainText())
            self.char_count_label.setText(f"{count} characters")

    def clear_error_styling(self):
        """Clear error styling when user starts typing."""
        if self.use_text_edit:
            self.input_field.setStyleSheet("")
        else:
            self.input_field.setStyleSheet("")

    def accept(self):
        """Handle OK button click."""
        if self.use_text_edit:
            value = self.input_field.toPlainText().strip()
        else:
            value = self.input_field.text().strip()

        if value:
            self.result_value = value
            # Store the configured value in the task
            self.task.configured_value = value
            super().accept()
        else:
            # Show error or keep dialog open
            if self.use_text_edit:
                self.input_field.setStyleSheet("border: 1px solid red;")
            else:
                self.input_field.setStyleSheet("border: 1px solid red;")

    def get_result(self):
        """Return the configured value."""
        return self.result_value


class LicenseSelectionDialog(QDialog):
    """Dialog for selecting a license."""

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.result_value = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Choose License")
        self.setModal(True)
        self.setFixedSize(500, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Choose License")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Description
        description = QLabel("Select a license for your project:")
        description.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(description)

        # License options
        self.license_combo = QComboBox()
        self.license_combo.setMinimumHeight(30)

        # Common licenses
        licenses = [
            ("MIT", "MIT License - Simple and permissive"),
            ("Apache 2.0", "Apache License 2.0 - Business-friendly"),
            ("GPL v3", "GNU General Public License v3 - Copyleft"),
            ("BSD 3-Clause", "BSD 3-Clause License - Permissive"),
            ("ISC", "ISC License - Simple and permissive"),
            ("Unlicense", "Unlicense - Public domain dedication"),
            ("Custom", "Custom license - Enter your own"),
        ]

        for license_name, description in licenses:
            self.license_combo.addItem(f"{license_name} - {description}")

        # Set current value if available
        if hasattr(self.task, "configured_value") and self.task.configured_value:
            # Find the index of the current license
            for i, (license_name, _) in enumerate(licenses):
                if license_name == self.task.configured_value:
                    self.license_combo.setCurrentIndex(i)
                    break

        layout.addWidget(self.license_combo)

        # License description area
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("""
            QLabel {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.description_label)

        # Update description when selection changes
        self.license_combo.currentIndexChanged.connect(self.update_description)
        self.update_description()  # Set initial description

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Set focus to combo box
        self.license_combo.setFocus()

    def update_description(self):
        """Update the license description based on selection."""
        current_text = self.license_combo.currentText()
        license_name = current_text.split(" - ")[0]

        descriptions = {
            "MIT": "The MIT License is a permissive license that allows for maximum freedom in using, modifying, and distributing the software. It's one of the most popular open source licenses.",
            "Apache 2.0": "The Apache License 2.0 is a permissive license that allows for commercial use, modification, distribution, and patent use. It provides an express grant of patent rights.",
            "GPL v3": "The GNU General Public License v3 is a copyleft license that ensures that derivative works are also open source. It requires that any modifications be shared under the same license.",
            "BSD 3-Clause": "The BSD 3-Clause License is a permissive license that allows for commercial use, modification, and distribution. It includes a clause about the use of the author's name for endorsement.",
            "ISC": "The ISC License is a permissive license similar to the MIT License. It's simple and allows for maximum freedom in using and distributing the software.",
            "Unlicense": "The Unlicense is a public domain dedication that allows for maximum freedom. It effectively places the software in the public domain.",
            "Custom": "You can specify your own custom license terms. This option allows for maximum flexibility but requires you to define the license terms yourself.",
        }

        self.description_label.setText(
            descriptions.get(license_name, "No description available.")
        )

    def accept(self):
        """Handle OK button click."""
        current_text = self.license_combo.currentText()
        license_name = current_text.split(" - ")[0]

        if license_name == "Custom":
            # For custom license, we could open another dialog, but for now just use the text
            self.result_value = "Custom License"
        else:
            self.result_value = license_name

        super().accept()

    def get_result(self):
        """Return the selected license."""
        return self.result_value


class PythonVersionDialog(QDialog):
    """Dialog for selecting Python version requirements."""

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.result_value = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Choose Python Version")
        self.setModal(True)
        self.setFixedSize(500, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Choose Python Version")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Description
        description = QLabel(
            "Select the minimum Python version required for your project:"
        )
        description.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(description)

        # Current Python version info
        import sys

        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        current_info = QLabel(f"Current Python version: {current_version}")
        current_info.setStyleSheet(
            "color: #4CAF50; font-weight: bold; margin-bottom: 10px;"
        )
        layout.addWidget(current_info)

        # Version selection
        version_label = QLabel("Minimum Python version:")
        layout.addWidget(version_label)

        # Version combo box
        self.version_combo = QComboBox()
        self.version_combo.setMinimumHeight(30)

        # Common Python versions (from oldest to newest)
        versions = [
            ("3.7", "Python 3.7 - End of life, not recommended"),
            ("3.8", "Python 3.8 - Widely supported"),
            ("3.9", "Python 3.9 - Good balance of features and support"),
            ("3.10", "Python 3.10 - Modern features, good support"),
            ("3.11", "Python 3.11 - Performance improvements"),
            ("3.12", "Python 3.12 - Latest stable"),
            ("3.13", "Python 3.13 - Current development"),
        ]

        for version, description in versions:
            self.version_combo.addItem(f"{version} - {description}")

        # Set current version as default
        current_major_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
        for i, (version, _) in enumerate(versions):
            if version == current_major_minor:
                self.version_combo.setCurrentIndex(i)
                break

        layout.addWidget(self.version_combo)

        # Custom version input
        custom_label = QLabel("Or specify custom version requirement:")
        layout.addWidget(custom_label)

        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("e.g., >=3.8, >=3.11, <4.0")
        self.custom_input.setMinimumHeight(30)
        layout.addWidget(self.custom_input)

        # Version description area
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.description_label)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Connect signals
        self.version_combo.currentTextChanged.connect(self.update_description)
        self.custom_input.textChanged.connect(self.on_custom_input_changed)

        # Set initial description
        self.update_description()

    def update_description(self):
        """Update the description based on selected version."""
        selected_text = self.version_combo.currentText()
        version = (
            selected_text.split(" - ")[0] if " - " in selected_text else selected_text
        )

        descriptions = {
            "3.7": "Python 3.7 reached end of life in June 2023. Not recommended for new projects.",
            "3.8": "Python 3.8 is widely supported and stable. Good choice for compatibility.",
            "3.9": "Python 3.9 offers modern features while maintaining broad compatibility.",
            "3.10": "Python 3.10 includes pattern matching and other modern features.",
            "3.11": "Python 3.11 provides significant performance improvements.",
            "3.12": "Python 3.12 is the latest stable release with newest features.",
            "3.13": "Python 3.13 is the current development version.",
        }

        description = descriptions.get(
            version, f"Python {version} - Modern Python version."
        )
        self.description_label.setText(description)

    def on_custom_input_changed(self):
        """Handle custom input changes."""
        if self.custom_input.text().strip():
            # If custom input is provided, update description
            custom_text = self.custom_input.text().strip()
            self.description_label.setText(f"Custom requirement: {custom_text}")
        else:
            # If custom input is empty, show description for combo selection
            self.update_description()

    def accept(self):
        """Handle OK button click."""
        # Check if custom input is provided
        custom_text = self.custom_input.text().strip()

        if custom_text:
            # Use custom input
            self.result_value = custom_text
        else:
            # Use combo selection
            selected_text = self.version_combo.currentText()
            version = (
                selected_text.split(" - ")[0]
                if " - " in selected_text
                else selected_text
            )
            self.result_value = f">={version}"

        # Store the configured value in the task
        self.task.configured_value = self.result_value
        super().accept()

    def get_result(self):
        """Return the configured value."""
        return self.result_value


class ClickableLabel(QLabel):
    """Clickable QLabel for task items with proper text alignment."""

    def __init__(self, task_description, parent=None):
        super().__init__(parent)
        self.task_description = task_description
        self.setup_ui()

    def setup_ui(self):
        """Setup the clickable label appearance and behavior."""
        # Set text with word wrapping and enable rich text
        self.setText(self.task_description)
        self.setWordWrap(True)
        self.setTextFormat(Qt.TextFormat.RichText)

        # Set alignment to left
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Set label properties
        self.setMinimumHeight(40)
        self.setMaximumHeight(80)

        # Make it look clickable with hover effect
        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 8px;
                color: #333;
            }
            QLabel:hover {
                background-color: #e0e0e0;
                border: 1px solid #999;
                border-radius: 4px;
            }
        """)

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_task_clicked()
        super().mousePressEvent(event)

    def on_task_clicked(self):
        """Handle task click."""
        # This method is not used anymore since we handle clicks in TaskItemWidget
        pass
        # TODO: Open child window for task configuration
        # This is where you would implement the child window opening
