"""Unit tests for task.py module."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QEvent, QPointF, Qt
from PyQt6.QtGui import QEnterEvent, QMouseEvent
from PyQt6.QtWidgets import QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QTextEdit

from new_python_github_project.task import (
    ClickableLabel,
    LicenseSelectionDialog,
    PythonVersionDialog,
    Task,
    TaskConfigDialog,
    TaskItemWidget,
)

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot  # pragma: no cover


class TestTask:
    """Test cases for Task class."""

    def test_init_default_values(self) -> None:
        """Test Task initialization with default values."""
        task = Task("Test description")

        assert task.description == "Test description"
        assert task.has_default is False
        assert task.is_completed is False
        assert task.default_value is None
        assert task.user_modified is False
        assert task.configured_value is None
        assert task.configured_values == {}

    def test_init_with_all_parameters(self) -> None:
        """Test Task initialization with all parameters specified."""
        task = Task(
            description="Test task",
            has_default=True,
            is_completed=True,
            default_value="default_val",
        )

        assert task.description == "Test task"
        assert task.has_default is True
        assert task.is_completed is True
        assert task.default_value == "default_val"
        assert task.user_modified is False
        assert task.configured_value is None
        assert task.configured_values == {}

    def test_status_property_completed_when_is_completed_true(self) -> None:
        """Test status property returns 'completed' when is_completed is True."""
        task = Task("Test task", is_completed=True)
        assert task.status == "completed"

    def test_status_property_completed_when_has_default_true(self) -> None:
        """Test status property returns 'completed' when has_default is True."""
        task = Task("Test task", has_default=True)
        assert task.status == "completed"

    def test_status_property_completed_when_both_true(self) -> None:
        """Test status property returns 'completed' when both conditions are True."""
        task = Task("Test task", has_default=True, is_completed=True)
        assert task.status == "completed"

    def test_status_property_pending_when_both_false(self) -> None:
        """Test status property returns 'pending' when both conditions are False."""
        task = Task("Test task", has_default=False, is_completed=False)
        assert task.status == "pending"

    def test_get_tooltip_text_pending_status(self) -> None:
        """Test get_tooltip_text returns 'User input required' for pending tasks."""
        task = Task("Test task", has_default=False, is_completed=False)
        assert task.get_tooltip_text() == "User input required"

    def test_get_tooltip_text_completed_user_modified(self) -> None:
        """Test get_tooltip_text returns 'Completed' for user-modified tasks."""
        task = Task("Test task", is_completed=True)
        task.user_modified = True
        assert task.get_tooltip_text() == "Completed"

    def test_get_tooltip_text_completed_not_user_modified(self) -> None:
        """Test get_tooltip_text returns 'Use default' for non-user-modified completed tasks."""
        task = Task("Test task", is_completed=True)
        task.user_modified = False
        assert task.get_tooltip_text() == "Use default"

    def test_get_tooltip_text_has_default_not_user_modified(self) -> None:
        """Test get_tooltip_text returns 'Use default' for tasks with defaults."""
        task = Task("Test task", has_default=True)
        task.user_modified = False
        assert task.get_tooltip_text() == "Use default"

    def test_truncate_path_short_path(self) -> None:
        """Test _truncate_path returns unchanged string for short paths."""
        task = Task("Test task")
        short_path = "/short/path"
        result = task._truncate_path(short_path)
        assert result == short_path

    def test_truncate_path_exactly_50_chars(self) -> None:
        """Test _truncate_path returns unchanged string for exactly 50 character paths."""
        task = Task("Test task")
        path_50_chars = "/some/path/" + "x" * 39  # Creates exactly 50 chars
        assert len(path_50_chars) == 50
        result = task._truncate_path(path_50_chars)
        assert result == path_50_chars

    def test_truncate_path_long_with_separator(self) -> None:
        """Test _truncate_path truncates at separator for long paths."""
        task = Task("Test task")
        long_path = "/very/long/path/that/exceeds/fifty/characters/and/has/more/directories/here"
        result = task._truncate_path(long_path)

        # Should find separator and truncate there
        assert result.startswith("...")
        assert "/" in result
        assert len(result) < len(long_path)

    def test_truncate_path_long_without_separator(self) -> None:
        """Test _truncate_path truncates at end when no separator found."""
        task = Task("Test task")
        long_path = "a" * 80  # No path separators
        result = task._truncate_path(long_path)

        assert result.startswith("...")
        assert result == "..." + long_path[-50:]

    def test_truncate_path_long_with_separator_at_boundary(self) -> None:
        """Test _truncate_path with separator exactly at search boundary."""
        task = Task("Test task")
        # Create path with separator at position 50
        long_path = "a" * 50 + "/some/more/path"
        result = task._truncate_path(long_path)

        assert result.startswith("...")
        assert result == "..." + long_path[50:]

    def test_truncate_path_long_with_separator_beyond_search_range(self) -> None:
        """Test _truncate_path when separator is beyond search range."""
        task = Task("Test task")
        # Create path with separator beyond 20-char search range
        long_path = "a" * 71 + "/end"  # Separator at position 71 (50 + 21)
        result = task._truncate_path(long_path)

        # Should use fallback truncation
        assert result.startswith("...")
        assert result == "..." + long_path[-50:]

    def test_get_display_text_pending_task(self) -> None:
        """Test get_display_text returns base description for pending tasks."""
        task = Task("Test description")
        result = task.get_display_text()
        assert result == "Test description"

    def test_get_display_text_completed_with_configured_value(self) -> None:
        """Test get_display_text shows configured value for completed tasks."""
        task = Task("Set project name", is_completed=True)
        task.configured_value = "MyProject"

        result = task.get_display_text()
        expected = "Set project name <span style='color: #FF8C00; font-style: italic;'>[MyProject]</span>"
        assert result == expected

    def test_get_display_text_completed_with_long_configured_value(self) -> None:
        """Test get_display_text truncates long configured values."""
        task = Task("Set directory", is_completed=True)
        long_path = "/very/long/path/that/exceeds/fifty/characters/and/needs/truncation"
        task.configured_value = long_path

        result = task.get_display_text()
        assert "Set directory" in result
        assert "<span style='color: #FF8C00; font-style: italic;'>" in result
        assert "..." in result  # Should be truncated

    def test_get_display_text_completed_with_configured_values(self) -> None:
        """Test get_display_text shows param count for multi-value tasks."""
        task = Task("Configure settings", is_completed=True)
        task.configured_values = {
            "param1": "value1",
            "param2": "value2",
            "param3": "value3",
        }

        result = task.get_display_text()
        expected = "Configure settings <span style='color: #FF8C00; font-style: italic;'>[3 params]</span>"
        assert result == expected

    def test_get_display_text_completed_with_default_value(self) -> None:
        """Test get_display_text shows default value when no configured value."""
        task = Task(
            "Use default setting", has_default=True, default_value="default_val"
        )

        result = task.get_display_text()
        expected = "Use default setting <span style='color: #FF8C00; font-style: italic;'>[default_val]</span>"
        assert result == expected

    def test_get_display_text_completed_with_long_default_value(self) -> None:
        """Test get_display_text truncates long default values."""
        task = Task("Use default path", has_default=True)
        long_default = (
            "/very/long/default/path/that/exceeds/fifty/characters/and/needs/truncation"
        )
        task.default_value = long_default

        result = task.get_display_text()
        assert "Use default path" in result
        assert "<span style='color: #FF8C00; font-style: italic;'>" in result
        assert "..." in result  # Should be truncated

    def test_get_display_text_completed_no_values(self) -> None:
        """Test get_display_text shows checkmark when no specific values."""
        task = Task("Simple task", is_completed=True)
        # No configured_value, configured_values, or default_value

        result = task.get_display_text()
        expected = (
            "Simple task <span style='color: #FF8C00; font-style: italic;'>[✓]</span>"
        )
        assert result == expected

    def test_get_display_text_completed_has_default_no_default_value(self) -> None:
        """Test get_display_text shows checkmark when has_default but no default_value."""
        task = Task("Task with default flag", has_default=True, default_value=None)

        result = task.get_display_text()
        expected = "Task with default flag <span style='color: #FF8C00; font-style: italic;'>[✓]</span>"
        assert result == expected

    def test_get_display_text_priority_configured_value_over_configured_values(
        self,
    ) -> None:
        """Test get_display_text prioritizes configured_value over configured_values."""
        task = Task("Priority test", is_completed=True)
        task.configured_value = "single_value"
        task.configured_values = {"param1": "value1", "param2": "value2"}

        result = task.get_display_text()
        expected = "Priority test <span style='color: #FF8C00; font-style: italic;'>[single_value]</span>"
        assert result == expected

    def test_get_display_text_priority_configured_values_over_default(self) -> None:
        """Test get_display_text prioritizes configured_values over default_value."""
        task = Task(
            "Priority test",
            has_default=True,
            default_value="default_val",
            is_completed=True,
        )
        task.configured_values = {"param1": "value1"}

        result = task.get_display_text()
        expected = "Priority test <span style='color: #FF8C00; font-style: italic;'>[1 params]</span>"
        assert result == expected


class TestClickableLabel:
    """Test cases for ClickableLabel class."""

    def test_init_with_task_description(self, qtbot: "QtBot") -> None:
        """Test ClickableLabel initialization with task description."""
        task_description = "Test task description"
        label = ClickableLabel(task_description)
        qtbot.addWidget(label)

        assert label.task_description == task_description
        assert isinstance(label, QLabel)

    def test_init_with_parent(self, qtbot: "QtBot") -> None:
        """Test ClickableLabel initialization with parent widget."""
        parent = QLabel()
        qtbot.addWidget(parent)

        task_description = "Test task with parent"
        label = ClickableLabel(task_description, parent)
        qtbot.addWidget(label)

        assert label.parent() == parent
        assert label.task_description == task_description

    def test_setup_ui_text_properties(self, qtbot: "QtBot") -> None:
        """Test setup_ui configures text properties correctly."""
        task_description = "Test task for UI setup"
        label = ClickableLabel(task_description)
        qtbot.addWidget(label)

        assert label.text() == task_description
        assert label.wordWrap() is True
        assert label.textFormat() == Qt.TextFormat.RichText

    def test_setup_ui_alignment(self, qtbot: "QtBot") -> None:
        """Test setup_ui configures alignment correctly."""
        label = ClickableLabel("Test alignment")
        qtbot.addWidget(label)

        expected_alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        assert label.alignment() == expected_alignment

    def test_setup_ui_size_constraints(self, qtbot: "QtBot") -> None:
        """Test setup_ui configures size constraints correctly."""
        label = ClickableLabel("Test size constraints")
        qtbot.addWidget(label)

        assert label.minimumHeight() == 40
        assert label.maximumHeight() == 80

    def test_setup_ui_mouse_tracking(self, qtbot: "QtBot") -> None:
        """Test setup_ui enables mouse tracking."""
        label = ClickableLabel("Test mouse tracking")
        qtbot.addWidget(label)

        assert label.hasMouseTracking() is True

    def test_setup_ui_stylesheet_applied(self, qtbot: "QtBot") -> None:
        """Test setup_ui applies correct stylesheet."""
        label = ClickableLabel("Test stylesheet")
        qtbot.addWidget(label)

        stylesheet = label.styleSheet()
        assert "QLabel" in stylesheet
        assert "background-color: transparent" in stylesheet
        assert "QLabel:hover" in stylesheet
        assert "background-color: #e0e0e0" in stylesheet

    def test_mouse_press_event_left_button(self, qtbot: "QtBot") -> None:
        """Test mousePressEvent handles left button clicks."""
        label = ClickableLabel("Test mouse press")
        qtbot.addWidget(label)

        # Mock the on_task_clicked method to verify it's called
        mock_method = MagicMock()
        label.on_task_clicked = mock_method  # type: ignore[method-assign]

        # Create a left button mouse press event
        pos = QPointF(label.rect().center())
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            pos,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        label.mousePressEvent(event)
        mock_method.assert_called_once()

    def test_mouse_press_event_right_button(self, qtbot: "QtBot") -> None:
        """Test mousePressEvent ignores right button clicks."""
        label = ClickableLabel("Test right click")
        qtbot.addWidget(label)

        # Mock the on_task_clicked method to verify it's not called
        mock_method = MagicMock()
        label.on_task_clicked = mock_method  # type: ignore[method-assign]

        # Create a right button mouse press event
        pos = QPointF(label.rect().center())
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            pos,
            Qt.MouseButton.RightButton,
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier,
        )

        label.mousePressEvent(event)
        mock_method.assert_not_called()

    def test_mouse_press_event_middle_button(self, qtbot: "QtBot") -> None:
        """Test mousePressEvent ignores middle button clicks."""
        label = ClickableLabel("Test middle click")
        qtbot.addWidget(label)

        # Mock the on_task_clicked method to verify it's not called
        mock_method = MagicMock()
        label.on_task_clicked = mock_method  # type: ignore[method-assign]

        # Create a middle button mouse press event
        pos = QPointF(label.rect().center())
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            pos,
            Qt.MouseButton.MiddleButton,
            Qt.MouseButton.MiddleButton,
            Qt.KeyboardModifier.NoModifier,
        )

        label.mousePressEvent(event)
        mock_method.assert_not_called()

    def test_on_task_clicked_implementation(self, qtbot: "QtBot") -> None:
        """Test on_task_clicked method exists and can be called."""
        label = ClickableLabel("Test task clicked")
        qtbot.addWidget(label)

        # Should not raise any exception
        label.on_task_clicked()

    def test_rich_text_formatting(self, qtbot: "QtBot") -> None:
        """Test that rich text formatting is supported."""
        rich_text = "<b>Bold</b> and <i>italic</i> text"
        label = ClickableLabel(rich_text)
        qtbot.addWidget(label)

        assert label.text() == rich_text
        assert label.textFormat() == Qt.TextFormat.RichText

    def test_empty_task_description(self, qtbot: "QtBot") -> None:
        """Test ClickableLabel with empty task description."""
        label = ClickableLabel("")
        qtbot.addWidget(label)

        assert label.task_description == ""
        assert label.text() == ""

    def test_long_task_description_wrapping(self, qtbot: "QtBot") -> None:
        """Test word wrapping with long task description."""
        long_description = "This is a very long task description that should wrap " * 10
        label = ClickableLabel(long_description)
        qtbot.addWidget(label)

        assert label.text() == long_description
        assert label.wordWrap() is True


class TestPythonVersionDialog:
    """Test cases for PythonVersionDialog class."""

    def test_init_with_task(self, qtbot: "QtBot") -> None:
        """Test PythonVersionDialog initialization with task."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        assert dialog.task == task
        assert dialog.result_value is None

    def test_init_with_parent(self, qtbot: "QtBot") -> None:
        """Test PythonVersionDialog initialization with parent widget."""
        parent = QLabel()
        qtbot.addWidget(parent)

        task = Task("Test task", False)
        dialog = PythonVersionDialog(task, parent)
        qtbot.addWidget(dialog)

        assert dialog.parent() == parent
        assert dialog.task == task

    def test_setup_ui_window_properties(self, qtbot: "QtBot") -> None:
        """Test setup_ui configures window properties correctly."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Choose Python Version"
        assert dialog.isModal() is True
        assert dialog.size().width() == 500
        assert dialog.size().height() == 400

    def test_setup_ui_components_exist(self, qtbot: "QtBot") -> None:
        """Test setup_ui creates all necessary UI components."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Check that components exist
        assert hasattr(dialog, "version_combo")
        assert hasattr(dialog, "custom_input")
        assert hasattr(dialog, "description_label")
        assert dialog.version_combo is not None
        assert dialog.custom_input is not None
        assert dialog.description_label is not None

    def test_version_combo_has_python_versions(self, qtbot: "QtBot") -> None:
        """Test version combo box contains expected Python versions."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Check that combo box has items
        assert dialog.version_combo.count() > 0

        # Check that it contains expected Python versions
        all_items = [
            dialog.version_combo.itemText(i)
            for i in range(dialog.version_combo.count())
        ]
        version_texts = " ".join(all_items)

        assert "3.7" in version_texts
        assert "3.8" in version_texts
        assert "3.9" in version_texts
        assert "3.10" in version_texts
        assert "3.11" in version_texts
        assert "3.12" in version_texts

    def test_custom_input_placeholder(self, qtbot: "QtBot") -> None:
        """Test custom input has appropriate placeholder text."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        placeholder = dialog.custom_input.placeholderText()
        assert ">=3.8" in placeholder or ">=3.11" in placeholder
        assert "<4.0" in placeholder

    def test_update_description_for_known_versions(self, qtbot: "QtBot") -> None:
        """Test update_description provides descriptions for known versions."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Test various version selections
        for i in range(dialog.version_combo.count()):
            dialog.version_combo.setCurrentIndex(i)
            dialog.update_description()
            description = dialog.description_label.text()
            assert description != ""
            assert "Python" in description

    def test_update_description_for_python_38(self, qtbot: "QtBot") -> None:
        """Test update_description for Python 3.8 specifically."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select Python 3.8
        for i in range(dialog.version_combo.count()):
            if "3.8" in dialog.version_combo.itemText(i):
                dialog.version_combo.setCurrentIndex(i)
                break

        dialog.update_description()
        description = dialog.description_label.text()
        assert "3.8" in description
        assert "supported" in description.lower() or "stable" in description.lower()

    def test_on_custom_input_changed_with_text(self, qtbot: "QtBot") -> None:
        """Test on_custom_input_changed when custom text is provided."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Set custom input
        custom_requirement = ">=3.9,<4.0"
        dialog.custom_input.setText(custom_requirement)
        dialog.on_custom_input_changed()

        description = dialog.description_label.text()
        assert "Custom requirement" in description
        assert custom_requirement in description

    def test_on_custom_input_changed_empty_text(self, qtbot: "QtBot") -> None:
        """Test on_custom_input_changed when custom text is empty."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Set and then clear custom input
        dialog.custom_input.setText(">=3.9")
        dialog.custom_input.setText("")
        dialog.on_custom_input_changed()

        description = dialog.description_label.text()
        assert "Custom requirement" not in description
        assert "Python" in description

    def test_accept_with_custom_input(self, qtbot: "QtBot") -> None:
        """Test accept method when custom input is provided."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        custom_requirement = ">=3.10,<4.0"
        dialog.custom_input.setText(custom_requirement)

        # Mock only super().accept() to prevent actual dialog closing
        with patch.object(dialog.__class__.__bases__[0], "accept"):
            dialog.accept()

        assert dialog.result_value == custom_requirement
        assert dialog.task.configured_value == custom_requirement

    def test_accept_with_combo_selection(self, qtbot: "QtBot") -> None:
        """Test accept method when using combo box selection."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Clear custom input and select from combo
        dialog.custom_input.setText("")

        # Find and select Python 3.9
        for i in range(dialog.version_combo.count()):
            if "3.9" in dialog.version_combo.itemText(i):
                dialog.version_combo.setCurrentIndex(i)
                break

        # Mock only super().accept() to prevent actual dialog closing
        with patch.object(dialog.__class__.__bases__[0], "accept"):
            dialog.accept()

        assert dialog.result_value == ">=3.9"
        assert dialog.task.configured_value == ">=3.9"

    def test_accept_with_custom_input_whitespace(self, qtbot: "QtBot") -> None:
        """Test accept method when custom input has whitespace."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Set custom input with leading/trailing whitespace
        dialog.custom_input.setText("  >=3.8  ")

        # Mock only super().accept() to prevent actual dialog closing
        with patch.object(dialog.__class__.__bases__[0], "accept"):
            dialog.accept()

        # Should strip whitespace
        assert dialog.result_value == ">=3.8"
        assert dialog.task.configured_value == ">=3.8"

    def test_accept_with_version_without_dash(self, qtbot: "QtBot") -> None:
        """Test accept method when combo text doesn't contain ' - '."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Clear custom input
        dialog.custom_input.setText("")

        # Manually set combo text without ' - ' separator
        dialog.version_combo.clear()
        dialog.version_combo.addItem("3.11")
        dialog.version_combo.setCurrentText("3.11")

        # Mock only super().accept() to prevent actual dialog closing
        with patch.object(dialog.__class__.__bases__[0], "accept"):
            dialog.accept()

        assert dialog.result_value == ">=3.11"
        assert dialog.task.configured_value == ">=3.11"

    def test_get_result_returns_configured_value(self, qtbot: "QtBot") -> None:
        """Test get_result returns the configured value."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Initially should return None
        assert dialog.get_result() is None

        # Set a result value
        test_value = ">=3.8"
        dialog.result_value = test_value
        assert dialog.get_result() == test_value

    def test_custom_input_signal_connection(self, qtbot: "QtBot") -> None:
        """Test that custom input text changes trigger description updates."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Change custom input and verify description updates
        original_description = dialog.description_label.text()

        dialog.custom_input.setText(">=3.11")
        # The signal should be connected and update description
        qtbot.wait(10)  # Small wait for signal processing

        new_description = dialog.description_label.text()
        assert "Custom requirement" in new_description
        assert ">=3.11" in new_description

    def test_version_combo_signal_connection(self, qtbot: "QtBot") -> None:
        """Test that combo box changes trigger description updates."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Change combo selection and verify description updates
        original_index = dialog.version_combo.currentIndex()
        new_index = (original_index + 1) % dialog.version_combo.count()

        dialog.version_combo.setCurrentIndex(new_index)
        qtbot.wait(10)  # Small wait for signal processing

        description = dialog.description_label.text()
        assert description != ""
        assert "Python" in description

    def test_dialog_has_ok_cancel_buttons(self, qtbot: "QtBot") -> None:
        """Test that dialog has OK and Cancel buttons."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        # Find button box in the dialog
        button_boxes = dialog.findChildren(QDialogButtonBox)
        assert len(button_boxes) > 0

        button_box = button_boxes[0]
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

        assert ok_button is not None
        assert cancel_button is not None

    def test_description_label_styling(self, qtbot: "QtBot") -> None:
        """Test that description label has proper styling."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        stylesheet = dialog.description_label.styleSheet()
        assert "background-color" in stylesheet
        assert "border" in stylesheet
        assert "padding" in stylesheet

    def test_word_wrap_enabled_on_description(self, qtbot: "QtBot") -> None:
        """Test that description label has word wrap enabled."""
        task = Task("Test task", False)
        dialog = PythonVersionDialog(task)
        qtbot.addWidget(dialog)

        assert dialog.description_label.wordWrap() is True


class TestLicenseSelectionDialog:
    """Test cases for LicenseSelectionDialog class."""

    def test_init_with_task(self, qtbot: "QtBot") -> None:
        """Test LicenseSelectionDialog initialization with task."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        assert dialog.task == task
        assert dialog.result_value is None

    def test_init_with_parent(self, qtbot: "QtBot") -> None:
        """Test LicenseSelectionDialog initialization with parent widget."""
        parent = QLabel()
        qtbot.addWidget(parent)

        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task, parent)
        qtbot.addWidget(dialog)

        assert dialog.parent() == parent
        assert dialog.task == task

    def test_setup_ui_window_properties(self, qtbot: "QtBot") -> None:
        """Test setup_ui configures window properties correctly."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Choose License"
        assert dialog.isModal() is True
        assert dialog.size().width() == 500
        assert dialog.size().height() == 400

    def test_setup_ui_components_exist(self, qtbot: "QtBot") -> None:
        """Test setup_ui creates all necessary UI components."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Check that components exist
        assert hasattr(dialog, "license_combo")
        assert hasattr(dialog, "description_label")
        assert dialog.license_combo is not None
        assert dialog.description_label is not None

    def test_license_combo_has_license_options(self, qtbot: "QtBot") -> None:
        """Test license combo box contains expected license options."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Check that combo box has items
        assert dialog.license_combo.count() > 0

        # Check that it contains expected licenses
        all_items = [
            dialog.license_combo.itemText(i)
            for i in range(dialog.license_combo.count())
        ]
        license_texts = " ".join(all_items)

        assert "MIT" in license_texts
        assert "Apache 2.0" in license_texts
        assert "GPL v3" in license_texts
        assert "BSD 3-Clause" in license_texts
        assert "ISC" in license_texts
        assert "Unlicense" in license_texts
        assert "Custom" in license_texts

    def test_setup_ui_with_existing_configured_value(self, qtbot: "QtBot") -> None:
        """Test setup_ui selects existing configured value if available."""
        task = Task("Test task", False)
        task.configured_value = "MIT"
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Should select MIT license
        current_text = dialog.license_combo.currentText()
        assert "MIT" in current_text

    def test_setup_ui_with_invalid_configured_value(self, qtbot: "QtBot") -> None:
        """Test setup_ui handles invalid configured value gracefully."""
        task = Task("Test task", False)
        task.configured_value = "NonExistentLicense"
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Should not crash and should have a valid selection
        assert dialog.license_combo.currentIndex() >= 0

    def test_setup_ui_with_no_configured_value(self, qtbot: "QtBot") -> None:
        """Test setup_ui when task has no configured_value attribute."""
        task = Task("Test task", False)
        # Don't set configured_value attribute
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Should not crash and should have a valid selection
        assert dialog.license_combo.currentIndex() >= 0

    def test_update_description_for_mit_license(self, qtbot: "QtBot") -> None:
        """Test update_description for MIT license specifically."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select MIT license
        for i in range(dialog.license_combo.count()):
            if "MIT" in dialog.license_combo.itemText(i):
                dialog.license_combo.setCurrentIndex(i)
                break

        dialog.update_description()
        description = dialog.description_label.text()
        assert "MIT" in description
        assert "permissive" in description.lower()

    def test_update_description_for_apache_license(self, qtbot: "QtBot") -> None:
        """Test update_description for Apache 2.0 license."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select Apache 2.0 license
        for i in range(dialog.license_combo.count()):
            if "Apache 2.0" in dialog.license_combo.itemText(i):
                dialog.license_combo.setCurrentIndex(i)
                break

        dialog.update_description()
        description = dialog.description_label.text()
        assert "Apache" in description
        assert "patent" in description.lower()

    def test_update_description_for_gpl_license(self, qtbot: "QtBot") -> None:
        """Test update_description for GPL v3 license."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select GPL v3 license
        for i in range(dialog.license_combo.count()):
            if "GPL v3" in dialog.license_combo.itemText(i):
                dialog.license_combo.setCurrentIndex(i)
                break

        dialog.update_description()
        description = dialog.description_label.text()
        assert "GPL" in description or "GNU" in description
        assert "copyleft" in description.lower()

    def test_update_description_for_bsd_license(self, qtbot: "QtBot") -> None:
        """Test update_description for BSD 3-Clause license."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select BSD 3-Clause license
        for i in range(dialog.license_combo.count()):
            if "BSD 3-Clause" in dialog.license_combo.itemText(i):
                dialog.license_combo.setCurrentIndex(i)
                break

        dialog.update_description()
        description = dialog.description_label.text()
        assert "BSD" in description
        assert "endorsement" in description.lower()

    def test_update_description_for_isc_license(self, qtbot: "QtBot") -> None:
        """Test update_description for ISC license."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select ISC license
        for i in range(dialog.license_combo.count()):
            if "ISC" in dialog.license_combo.itemText(i):
                dialog.license_combo.setCurrentIndex(i)
                break

        dialog.update_description()
        description = dialog.description_label.text()
        assert "ISC" in description
        assert "permissive" in description.lower()

    def test_update_description_for_unlicense(self, qtbot: "QtBot") -> None:
        """Test update_description for Unlicense."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select Unlicense
        for i in range(dialog.license_combo.count()):
            if "Unlicense" in dialog.license_combo.itemText(i):
                dialog.license_combo.setCurrentIndex(i)
                break

        dialog.update_description()
        description = dialog.description_label.text()
        assert "Unlicense" in description
        assert "public domain" in description.lower()

    def test_update_description_for_custom_license(self, qtbot: "QtBot") -> None:
        """Test update_description for Custom license."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select Custom license
        for i in range(dialog.license_combo.count()):
            if "Custom" in dialog.license_combo.itemText(i):
                dialog.license_combo.setCurrentIndex(i)
                break

        dialog.update_description()
        description = dialog.description_label.text()
        assert "custom" in description.lower()
        assert "flexibility" in description.lower()

    def test_update_description_for_unknown_license(self, qtbot: "QtBot") -> None:
        """Test update_description for unknown license."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Manually set an unknown license
        dialog.license_combo.clear()
        dialog.license_combo.addItem("Unknown License - Description")
        dialog.update_description()

        description = dialog.description_label.text()
        assert "No description available" in description

    def test_accept_with_standard_license(self, qtbot: "QtBot") -> None:
        """Test accept method with standard license selection."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select MIT license
        for i in range(dialog.license_combo.count()):
            if "MIT" in dialog.license_combo.itemText(i):
                dialog.license_combo.setCurrentIndex(i)
                break

        # Mock super().accept() to prevent actual dialog closing
        with patch.object(dialog.__class__.__bases__[0], "accept"):
            dialog.accept()

        assert dialog.result_value == "MIT"

    def test_accept_with_custom_license(self, qtbot: "QtBot") -> None:
        """Test accept method with custom license selection."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find and select Custom license
        for i in range(dialog.license_combo.count()):
            if "Custom" in dialog.license_combo.itemText(i):
                dialog.license_combo.setCurrentIndex(i)
                break

        # Mock super().accept() to prevent actual dialog closing
        with patch.object(dialog.__class__.__bases__[0], "accept"):
            dialog.accept()

        assert dialog.result_value == "Custom License"

    def test_get_result_returns_selected_value(self, qtbot: "QtBot") -> None:
        """Test get_result returns the selected license value."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Initially should return None
        assert dialog.get_result() is None

        # Set a result value
        test_value = "Apache 2.0"
        dialog.result_value = test_value
        assert dialog.get_result() == test_value

    def test_license_combo_signal_connection(self, qtbot: "QtBot") -> None:
        """Test that combo box changes trigger description updates."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Change combo selection and verify description updates
        original_index = dialog.license_combo.currentIndex()
        new_index = (original_index + 1) % dialog.license_combo.count()

        dialog.license_combo.setCurrentIndex(new_index)
        qtbot.wait(10)  # Small wait for signal processing

        description = dialog.description_label.text()
        assert description != ""
        assert len(description) > 10  # Should have meaningful description

    def test_dialog_has_ok_cancel_buttons(self, qtbot: "QtBot") -> None:
        """Test that dialog has OK and Cancel buttons."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Find button box in the dialog
        button_boxes = dialog.findChildren(QDialogButtonBox)
        assert len(button_boxes) > 0

        button_box = button_boxes[0]
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

        assert ok_button is not None
        assert cancel_button is not None

    def test_description_label_styling(self, qtbot: "QtBot") -> None:
        """Test that description label has proper styling."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        stylesheet = dialog.description_label.styleSheet()
        assert "background-color" in stylesheet
        assert "border" in stylesheet
        assert "padding" in stylesheet

    def test_word_wrap_enabled_on_description(self, qtbot: "QtBot") -> None:
        """Test that description label has word wrap enabled."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        assert dialog.description_label.wordWrap() is True

    def test_license_combo_has_focus(self, qtbot: "QtBot") -> None:
        """Test that license combo box receives focus on setup."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Show the dialog to properly set focus
        dialog.show()
        with qtbot.waitExposed(dialog):
            pass

        # The combo box should have focus (or be focusable)
        assert (
            dialog.license_combo.hasFocus()
            or dialog.license_combo.focusPolicy() != Qt.FocusPolicy.NoFocus
        )

    def test_initial_description_is_set(self, qtbot: "QtBot") -> None:
        """Test that initial description is set during setup."""
        task = Task("Test task", False)
        dialog = LicenseSelectionDialog(task)
        qtbot.addWidget(dialog)

        # Description should be set automatically
        description = dialog.description_label.text()
        assert description != ""
        assert len(description) > 10  # Should have meaningful description


class TestTaskConfigDialog:
    """Test cases for TaskConfigDialog class."""

    def test_init_with_task(self, qtbot: "QtBot") -> None:
        """Test TaskConfigDialog initialization with task."""
        task = Task("Test task", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        assert dialog.task == task
        assert dialog.result_value is None

    def test_init_with_parent(self, qtbot: "QtBot") -> None:
        """Test TaskConfigDialog initialization with parent widget."""
        parent = QLabel()
        qtbot.addWidget(parent)

        task = Task("Test task", False)
        dialog = TaskConfigDialog(task, parent)
        qtbot.addWidget(dialog)

        assert dialog.parent() == parent
        assert dialog.task == task

    def test_setup_ui_project_description_task(self, qtbot: "QtBot") -> None:
        """Test setup_ui for project description task with text edit."""
        task = Task("Set project description", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Check window properties for description task
        assert dialog.windowTitle() == "Configure: Set project description"
        assert dialog.isModal() is True
        assert dialog.size().width() == 500
        assert dialog.size().height() == 300

        # Check that it uses text edit
        assert dialog.use_text_edit is True
        assert isinstance(dialog.input_field, QTextEdit)
        assert hasattr(dialog, "char_count_label")

    def test_setup_ui_author_name_task(self, qtbot: "QtBot") -> None:
        """Test setup_ui for author name task with line edit."""
        task = Task("Set author name", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Check window properties for author name task
        assert dialog.windowTitle() == "Configure: Set author name"
        assert dialog.isModal() is True
        assert dialog.size().width() == 400
        assert dialog.size().height() == 200

        # Check that it uses line edit
        assert dialog.use_text_edit is False
        assert isinstance(dialog.input_field, QLineEdit)
        assert not hasattr(dialog, "char_count_label")

    def test_setup_ui_project_name_task(self, qtbot: "QtBot") -> None:
        """Test setup_ui for project name task (default case)."""
        task = Task("Set project name", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Check window properties for project name task
        assert dialog.windowTitle() == "Configure: Set project name"
        assert dialog.isModal() is True
        assert dialog.size().width() == 400
        assert dialog.size().height() == 200

        # Check that it uses line edit (default case)
        assert dialog.use_text_edit is False
        assert isinstance(dialog.input_field, QLineEdit)

    def test_setup_ui_with_existing_configured_value_text_edit(
        self, qtbot: "QtBot"
    ) -> None:
        """Test setup_ui pre-fills existing value for text edit."""
        task = Task("Set project description", False)
        task.configured_value = "Existing description"
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        assert isinstance(dialog.input_field, QTextEdit)
        assert dialog.input_field.toPlainText() == "Existing description"

    def test_setup_ui_with_existing_configured_value_line_edit(
        self, qtbot: "QtBot"
    ) -> None:
        """Test setup_ui pre-fills existing value for line edit."""
        task = Task("Set author name", False)
        task.configured_value = "John Doe"
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        assert isinstance(dialog.input_field, QLineEdit)
        assert dialog.input_field.text() == "John Doe"
        # Text should be selected for easy replacement
        assert dialog.input_field.hasSelectedText()

    def test_setup_ui_with_no_configured_value(self, qtbot: "QtBot") -> None:
        """Test setup_ui when task has no configured_value attribute."""
        task = Task("Test task", False)
        # Don't set configured_value attribute
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Should not crash and should have empty field
        assert isinstance(dialog.input_field, QLineEdit)
        assert dialog.input_field.text() == ""

    def test_placeholder_texts(self, qtbot: "QtBot") -> None:
        """Test that appropriate placeholder texts are set."""
        # Test description task
        desc_task = Task("Set project description", False)
        desc_dialog = TaskConfigDialog(desc_task)
        qtbot.addWidget(desc_dialog)
        assert (
            "description of your project" in desc_dialog.input_field.placeholderText()
        )

        # Test author name task
        author_task = Task("Set author name", False)
        author_dialog = TaskConfigDialog(author_task)
        qtbot.addWidget(author_dialog)
        assert "author name" in author_dialog.input_field.placeholderText()

        # Test project name task (default)
        name_task = Task("Set project name", False)
        name_dialog = TaskConfigDialog(name_task)
        qtbot.addWidget(name_dialog)
        assert "project name" in name_dialog.input_field.placeholderText()

    def test_update_char_count_for_description(self, qtbot: "QtBot") -> None:
        """Test character count update for description task."""
        task = Task("Set project description", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Initially should show 0 characters
        assert dialog.char_count_label.text() == "0 characters"

        # Set some text and update
        assert isinstance(dialog.input_field, QTextEdit)
        dialog.input_field.setPlainText("Hello World")
        dialog.update_char_count()

        assert dialog.char_count_label.text() == "11 characters"

    def test_update_char_count_without_label(self, qtbot: "QtBot") -> None:
        """Test update_char_count when char_count_label doesn't exist."""
        task = Task("Set author name", False)  # Non-description task
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Should not crash when called on non-description dialog
        dialog.update_char_count()  # Should do nothing

    def test_clear_error_styling_text_edit(self, qtbot: "QtBot") -> None:
        """Test clear_error_styling for text edit field."""
        task = Task("Set project description", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Set error styling
        dialog.input_field.setStyleSheet("border: 1px solid red;")
        assert "red" in dialog.input_field.styleSheet()

        # Clear error styling
        dialog.clear_error_styling()
        assert dialog.input_field.styleSheet() == ""

    def test_clear_error_styling_line_edit(self, qtbot: "QtBot") -> None:
        """Test clear_error_styling for line edit field."""
        task = Task("Set author name", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Set error styling
        dialog.input_field.setStyleSheet("border: 1px solid red;")
        assert "red" in dialog.input_field.styleSheet()

        # Clear error styling
        dialog.clear_error_styling()
        assert dialog.input_field.styleSheet() == ""

    def test_accept_with_valid_text_edit_input(self, qtbot: "QtBot") -> None:
        """Test accept method with valid text edit input."""
        task = Task("Set project description", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Set valid input
        assert isinstance(dialog.input_field, QTextEdit)
        dialog.input_field.setPlainText("  Valid description  ")

        # Mock super().accept() to prevent actual dialog closing
        with patch.object(dialog.__class__.__bases__[0], "accept"):
            dialog.accept()

        # Should strip whitespace and store value
        assert dialog.result_value == "Valid description"
        assert dialog.task.configured_value == "Valid description"

    def test_accept_with_valid_line_edit_input(self, qtbot: "QtBot") -> None:
        """Test accept method with valid line edit input."""
        task = Task("Set author name", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Set valid input
        assert isinstance(dialog.input_field, QLineEdit)
        dialog.input_field.setText("  John Doe  ")

        # Mock super().accept() to prevent actual dialog closing
        with patch.object(dialog.__class__.__bases__[0], "accept"):
            dialog.accept()

        # Should strip whitespace and store value
        assert dialog.result_value == "John Doe"
        assert dialog.task.configured_value == "John Doe"

    def test_accept_with_empty_text_edit_input(self, qtbot: "QtBot") -> None:
        """Test accept method with empty text edit input."""
        task = Task("Set project description", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Set empty input
        assert isinstance(dialog.input_field, QTextEdit)
        dialog.input_field.setPlainText("   ")  # Only whitespace

        dialog.accept()

        # Should show error styling and not close dialog
        assert "red" in dialog.input_field.styleSheet()
        assert dialog.result_value is None

    def test_accept_with_empty_line_edit_input(self, qtbot: "QtBot") -> None:
        """Test accept method with empty line edit input."""
        task = Task("Set author name", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Set empty input
        assert isinstance(dialog.input_field, QLineEdit)
        dialog.input_field.setText("   ")  # Only whitespace

        dialog.accept()

        # Should show error styling and not close dialog
        assert "red" in dialog.input_field.styleSheet()
        assert dialog.result_value is None

    def test_get_result_returns_configured_value(self, qtbot: "QtBot") -> None:
        """Test get_result returns the configured value."""
        task = Task("Test task", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Initially should return None
        assert dialog.get_result() is None

        # Set a result value
        test_value = "Test result"
        dialog.result_value = test_value
        assert dialog.get_result() == test_value

    def test_signal_connections_text_edit(self, qtbot: "QtBot") -> None:
        """Test that signal connections work for text edit."""
        task = Task("Set project description", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Test character count signal
        assert isinstance(dialog.input_field, QTextEdit)
        dialog.input_field.setPlainText("Test")
        qtbot.wait(10)  # Small wait for signal processing

        assert "4 characters" in dialog.char_count_label.text()

    def test_signal_connections_line_edit(self, qtbot: "QtBot") -> None:
        """Test that signal connections work for line edit."""
        task = Task("Set author name", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Set error styling first
        dialog.input_field.setStyleSheet("border: 1px solid red;")
        assert "red" in dialog.input_field.styleSheet()

        # Change text should clear styling
        assert isinstance(dialog.input_field, QLineEdit)
        dialog.input_field.setText("New text")
        qtbot.wait(10)  # Small wait for signal processing

        # Error styling should be cleared
        assert dialog.input_field.styleSheet() == ""

    def test_dialog_has_ok_cancel_buttons(self, qtbot: "QtBot") -> None:
        """Test that dialog has OK and Cancel buttons."""
        task = Task("Test task", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Find button box in the dialog
        button_boxes = dialog.findChildren(QDialogButtonBox)
        assert len(button_boxes) > 0

        button_box = button_boxes[0]
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)

        assert ok_button is not None
        assert cancel_button is not None

    def test_input_field_has_focus(self, qtbot: "QtBot") -> None:
        """Test that input field receives focus on setup."""
        task = Task("Test task", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Show the dialog to properly set focus
        dialog.show()
        with qtbot.waitExposed(dialog):
            pass

        # The input field should have focus (or be focusable)
        assert (
            dialog.input_field.hasFocus()
            or dialog.input_field.focusPolicy() != Qt.FocusPolicy.NoFocus
        )

    def test_title_label_configuration(self, qtbot: "QtBot") -> None:
        """Test that title label is configured correctly."""
        task = Task("Custom Task Name", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        # Find title label
        title_labels = [
            child
            for child in dialog.findChildren(QLabel)
            if "Configure: Custom Task Name" in child.text()
        ]
        assert len(title_labels) > 0

        title_label = title_labels[0]
        font = title_label.font()
        assert font.bold()
        assert font.pointSize() == 14

    def test_input_label_text_for_different_tasks(self, qtbot: "QtBot") -> None:
        """Test that input labels have correct text for different task types."""
        # Description task
        desc_task = Task("Set project description", False)
        desc_dialog = TaskConfigDialog(desc_task)
        qtbot.addWidget(desc_dialog)
        assert desc_dialog.input_label.text() == "Project description:"

        # Author name task
        author_task = Task("Set author name", False)
        author_dialog = TaskConfigDialog(author_task)
        qtbot.addWidget(author_dialog)
        assert author_dialog.input_label.text() == "Author name:"

        # Default case (project name)
        name_task = Task("Set project name", False)
        name_dialog = TaskConfigDialog(name_task)
        qtbot.addWidget(name_dialog)
        assert name_dialog.input_label.text() == "Project name:"

    def test_text_edit_maximum_height(self, qtbot: "QtBot") -> None:
        """Test that text edit has correct maximum height."""
        task = Task("Set project description", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        assert isinstance(dialog.input_field, QTextEdit)
        assert dialog.input_field.maximumHeight() == 100

    def test_line_edit_minimum_height(self, qtbot: "QtBot") -> None:
        """Test that line edit has correct minimum height."""
        task = Task("Set author name", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        assert isinstance(dialog.input_field, QLineEdit)
        assert dialog.input_field.minimumHeight() == 30

    def test_char_count_label_styling(self, qtbot: "QtBot") -> None:
        """Test that character count label has correct styling."""
        task = Task("Set project description", False)
        dialog = TaskConfigDialog(task)
        qtbot.addWidget(dialog)

        stylesheet = dialog.char_count_label.styleSheet()
        assert "color: #666" in stylesheet
        assert "font-size: 11px" in stylesheet


class TestTaskItemWidget:
    """Test cases for TaskItemWidget class."""

    def test_init_with_task(self, qtbot: "QtBot") -> None:
        """Test TaskItemWidget initialization with task."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        assert widget.task == task

    def test_init_with_parent(self, qtbot: "QtBot") -> None:
        """Test TaskItemWidget initialization with parent widget."""
        parent = QLabel()
        qtbot.addWidget(parent)

        task = Task("Test task", False)
        widget = TaskItemWidget(task, parent)
        qtbot.addWidget(widget)

        assert widget.parent() == parent
        assert widget.task == task

    def test_setup_ui_creates_components(self, qtbot: "QtBot") -> None:
        """Test setup_ui creates all necessary UI components."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Check that components exist
        assert hasattr(widget, "status_label")
        assert hasattr(widget, "task_label")
        assert widget.status_label is not None
        assert widget.task_label is not None
        assert isinstance(widget.task_label, ClickableLabel)

    def test_setup_ui_layout_configuration(self, qtbot: "QtBot") -> None:
        """Test setup_ui configures layout correctly."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        layout = widget.layout()
        assert isinstance(layout, QHBoxLayout)
        assert layout.contentsMargins().left() == 5
        assert layout.spacing() == 10

    def test_setup_ui_status_label_size(self, qtbot: "QtBot") -> None:
        """Test setup_ui configures status label size correctly."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        assert widget.status_label.size().width() == 28
        assert widget.status_label.size().height() == 28

    def test_setup_ui_mouse_tracking_enabled(self, qtbot: "QtBot") -> None:
        """Test setup_ui enables mouse tracking."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        assert widget.hasMouseTracking() is True

    def test_setup_ui_styling_applied(self, qtbot: "QtBot") -> None:
        """Test setup_ui applies correct styling."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        stylesheet = widget.styleSheet()
        assert "background-color: #f8f8f8" in stylesheet
        assert "border: 1px solid #ddd" in stylesheet
        assert "border-radius: 4px" in stylesheet
        assert "QToolTip" in stylesheet

    def test_update_status_icon_completed_task(self, qtbot: "QtBot") -> None:
        """Test update_status_icon for completed task."""
        task = Task("Test task", False)
        task.is_completed = True  # This will make status return "completed"
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        widget.update_status_icon()

        assert widget.status_label.text() == "✓"
        stylesheet = widget.status_label.styleSheet()
        assert "color: #4CAF50" in stylesheet
        assert "font-weight: bold" in stylesheet
        assert "font-size: 20px" in stylesheet

    def test_update_status_icon_incomplete_task(self, qtbot: "QtBot") -> None:
        """Test update_status_icon for incomplete task."""
        task = Task("Test task", False)
        # Task is already pending by default (has_default=False, is_completed=False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        widget.update_status_icon()

        assert widget.status_label.text() == "?"
        stylesheet = widget.status_label.styleSheet()
        assert "color: #f44336" in stylesheet
        assert "font-weight: bold" in stylesheet
        assert "font-size: 20px" in stylesheet

    def test_mark_as_completed(self, qtbot: "QtBot") -> None:
        """Test mark_as_completed method."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        widget.mark_as_completed()

        assert task.is_completed is True
        assert task.user_modified is True
        assert widget.status_label.text() == "✓"

    def test_mark_as_using_default(self, qtbot: "QtBot") -> None:
        """Test mark_as_using_default method."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        widget.mark_as_using_default()

        assert task.is_completed is True
        assert task.user_modified is False
        assert widget.status_label.text() == "✓"

    def test_update_task_label(self, qtbot: "QtBot") -> None:
        """Test update_task_label updates the task label text."""
        task = Task("Original description", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock get_display_text to return a specific value
        with patch.object(task, "get_display_text", return_value="Updated description"):
            widget.update_task_label()

        assert widget.task_label.text() == "Updated description"

    def test_mouse_press_event_left_button(self, qtbot: "QtBot") -> None:
        """Test mousePressEvent handles left button clicks."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock the on_task_clicked method to verify it's called
        mock_method = MagicMock()
        widget.on_task_clicked = mock_method  # type: ignore[method-assign]

        # Create a left button mouse press event
        pos = QPointF(widget.rect().center())
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            pos,
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        widget.mousePressEvent(event)
        mock_method.assert_called_once()

    def test_mouse_press_event_right_button(self, qtbot: "QtBot") -> None:
        """Test mousePressEvent ignores right button clicks."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock the on_task_clicked method to verify it's not called
        mock_method = MagicMock()
        widget.on_task_clicked = mock_method  # type: ignore[method-assign]

        # Create a right button mouse press event
        pos = QPointF(widget.rect().center())
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            pos,
            Qt.MouseButton.RightButton,
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier,
        )

        widget.mousePressEvent(event)
        mock_method.assert_not_called()

    def test_event_filter_enter_event(self, qtbot: "QtBot") -> None:
        """Test eventFilter handles Enter events for tooltip."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock show_custom_tooltip
        mock_show = MagicMock()
        widget.show_custom_tooltip = mock_show  # type: ignore[method-assign]

        # Create an Enter event
        enter_event = QEnterEvent(QPointF(10, 10), QPointF(100, 100), QPointF(200, 200))
        enter_event.type = lambda: QEvent.Type.Enter  # type: ignore[method-assign]

        result = widget.eventFilter(widget.status_label, enter_event)

        assert result is True
        mock_show.assert_called_once_with(enter_event)

    def test_event_filter_leave_event(self, qtbot: "QtBot") -> None:
        """Test eventFilter handles Leave events for tooltip."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock hide_custom_tooltip
        mock_hide = MagicMock()
        widget.hide_custom_tooltip = mock_hide  # type: ignore[method-assign]

        # Create a Leave event
        leave_event = QEvent(QEvent.Type.Leave)

        result = widget.eventFilter(widget.status_label, leave_event)

        assert result is True
        mock_hide.assert_called_once()

    def test_event_filter_other_events(self, qtbot: "QtBot") -> None:
        """Test eventFilter passes through other events."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Create a different event type
        other_event = QEvent(QEvent.Type.Paint)

        result = widget.eventFilter(widget.status_label, other_event)

        assert result is False

    def test_show_custom_tooltip(self, qtbot: "QtBot") -> None:
        """Test show_custom_tooltip creates and shows tooltip."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock get_tooltip_text
        with patch.object(task, "get_tooltip_text", return_value="Test tooltip"):
            # Create a mock event with globalPos
            mock_event = MagicMock()
            mock_pos = MagicMock()
            mock_pos.x.return_value = 100
            mock_pos.y.return_value = 200
            mock_event.globalPos.return_value = mock_pos

            widget.show_custom_tooltip(mock_event)

            assert widget.custom_tooltip is not None
            assert widget.custom_tooltip.text() == "Test tooltip"

    def test_hide_custom_tooltip(self, qtbot: "QtBot") -> None:
        """Test hide_custom_tooltip hides and clears tooltip."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # First create a tooltip
        widget.custom_tooltip = QLabel("Test tooltip")

        widget.hide_custom_tooltip()

        assert widget.custom_tooltip is None

    def test_hide_custom_tooltip_when_none(self, qtbot: "QtBot") -> None:
        """Test hide_custom_tooltip when tooltip is None."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Ensure tooltip is None
        widget.custom_tooltip = None

        # Should not crash
        widget.hide_custom_tooltip()

        assert widget.custom_tooltip is None

    @patch("new_python_github_project.task.logging")
    def test_on_task_clicked_project_name(
        self, mock_logging: MagicMock, qtbot: "QtBot"
    ) -> None:
        """Test on_task_clicked for project name task."""
        task = Task("Set project name", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock the dialog
        with patch(
            "new_python_github_project.task.TaskConfigDialog"
        ) as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog.exec.return_value = 1  # QDialog.DialogCode.Accepted
            mock_dialog.get_result.return_value = "MyProject"
            mock_dialog_class.return_value = mock_dialog

            widget.on_task_clicked()

            # Verify dialog was created and executed
            mock_dialog_class.assert_called_once_with(task, widget)
            mock_dialog.exec.assert_called_once()
            mock_dialog.get_result.assert_called_once()

            # Verify task was marked as completed
            assert task.is_completed is True
            assert task.configured_value == "MyProject"

            # Verify logging
            mock_logging.info.assert_any_call("Task selected: Set project name")
            mock_logging.info.assert_any_call("Project name configured: MyProject")

    @patch("new_python_github_project.task.logging")
    @patch("new_python_github_project.task.QFileDialog")
    def test_on_task_clicked_project_directory(
        self, mock_file_dialog: MagicMock, mock_logging: MagicMock, qtbot: "QtBot"
    ) -> None:
        """Test on_task_clicked for project directory task."""
        task = Task("Set project directory", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock directory selection
        mock_file_dialog.getExistingDirectory.return_value = "/path/to/project"

        widget.on_task_clicked()

        # Verify directory dialog was called
        mock_file_dialog.getExistingDirectory.assert_called_once()

        # Verify task was marked as completed
        assert task.is_completed is True
        assert task.configured_value == "/path/to/project"

        # Verify logging
        mock_logging.info.assert_any_call("Task selected: Set project directory")
        mock_logging.info.assert_any_call("Project directory set to: /path/to/project")

    @patch("new_python_github_project.task.logging")
    @patch("new_python_github_project.task.QFileDialog")
    def test_on_task_clicked_project_directory_cancelled(
        self, mock_file_dialog: MagicMock, mock_logging: MagicMock, qtbot: "QtBot"
    ) -> None:
        """Test on_task_clicked for project directory task when cancelled."""
        task = Task("Set project directory", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock directory selection cancelled
        mock_file_dialog.getExistingDirectory.return_value = ""

        widget.on_task_clicked()

        # Verify task was not marked as completed
        assert task.is_completed is False
        assert not hasattr(task, "configured_value") or task.configured_value is None

        # Verify logging
        mock_logging.info.assert_any_call("Task selected: Set project directory")
        mock_logging.info.assert_any_call("Directory selection cancelled")

    @patch("new_python_github_project.task.logging")
    def test_on_task_clicked_choose_license(
        self, mock_logging: MagicMock, qtbot: "QtBot"
    ) -> None:
        """Test on_task_clicked for choose license task."""
        task = Task("Choose license", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock the dialog
        with patch(
            "new_python_github_project.task.LicenseSelectionDialog"
        ) as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog.exec.return_value = 1  # QDialog.DialogCode.Accepted
            mock_dialog.get_result.return_value = "MIT"
            mock_dialog_class.return_value = mock_dialog

            widget.on_task_clicked()

            # Verify dialog was created and executed
            mock_dialog_class.assert_called_once_with(task, widget)
            mock_dialog.exec.assert_called_once()
            mock_dialog.get_result.assert_called_once()

            # Verify task was marked as completed
            assert task.is_completed is True
            assert task.configured_value == "MIT"

            # Verify logging
            mock_logging.info.assert_any_call("Task selected: Choose license")
            mock_logging.info.assert_any_call("License selected: MIT")

    @patch("new_python_github_project.task.logging")
    def test_on_task_clicked_python_version(
        self, mock_logging: MagicMock, qtbot: "QtBot"
    ) -> None:
        """Test on_task_clicked for Python version task."""
        task = Task("Choose Python version", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock the dialog
        with patch(
            "new_python_github_project.task.PythonVersionDialog"
        ) as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog.exec.return_value = 1  # QDialog.DialogCode.Accepted
            mock_dialog.get_result.return_value = ">=3.9"
            mock_dialog_class.return_value = mock_dialog

            widget.on_task_clicked()

            # Verify dialog was created and executed
            mock_dialog_class.assert_called_once_with(task, widget)
            mock_dialog.exec.assert_called_once()
            mock_dialog.get_result.assert_called_once()

            # Verify task was marked as completed
            assert task.is_completed is True
            assert task.configured_value == ">=3.9"

            # Verify logging
            mock_logging.info.assert_any_call("Task selected: Choose Python version")
            mock_logging.info.assert_any_call("Python version configured: >=3.9")

    @patch("new_python_github_project.task.logging")
    def test_on_task_clicked_project_description(
        self, mock_logging: MagicMock, qtbot: "QtBot"
    ) -> None:
        """Test on_task_clicked for project description task."""
        task = Task("Set project description", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock the dialog
        with patch(
            "new_python_github_project.task.TaskConfigDialog"
        ) as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog.exec.return_value = 1  # QDialog.DialogCode.Accepted
            mock_dialog.get_result.return_value = "A great project"
            mock_dialog_class.return_value = mock_dialog

            widget.on_task_clicked()

            # Verify dialog was created and executed
            mock_dialog_class.assert_called_once_with(task, widget)
            mock_dialog.exec.assert_called_once()
            mock_dialog.get_result.assert_called_once()

            # Verify task was marked as completed
            assert task.is_completed is True
            assert task.configured_value == "A great project"

            # Verify logging
            mock_logging.info.assert_any_call("Task selected: Set project description")
            mock_logging.info.assert_any_call(
                "Project description configured: A great project"
            )

    @patch("new_python_github_project.task.logging")
    def test_on_task_clicked_author_name(
        self, mock_logging: MagicMock, qtbot: "QtBot"
    ) -> None:
        """Test on_task_clicked for author name task."""
        task = Task("Set author name", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock the dialog
        with patch(
            "new_python_github_project.task.TaskConfigDialog"
        ) as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog.exec.return_value = 1  # QDialog.DialogCode.Accepted
            mock_dialog.get_result.return_value = "John Doe"
            mock_dialog_class.return_value = mock_dialog

            widget.on_task_clicked()

            # Verify dialog was created and executed
            mock_dialog_class.assert_called_once_with(task, widget)
            mock_dialog.exec.assert_called_once()
            mock_dialog.get_result.assert_called_once()

            # Verify task was marked as completed
            assert task.is_completed is True
            assert task.configured_value == "John Doe"

            # Verify logging
            mock_logging.info.assert_any_call("Task selected: Set author name")
            mock_logging.info.assert_any_call("Author name configured: John Doe")

    @patch("new_python_github_project.task.logging")
    def test_on_task_clicked_unknown_task(
        self, mock_logging: MagicMock, qtbot: "QtBot"
    ) -> None:
        """Test on_task_clicked for unknown task type."""
        task = Task("Unknown task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        widget.on_task_clicked()

        # Verify task was not marked as completed
        assert task.is_completed is False

        # Verify logging
        mock_logging.info.assert_any_call("Task selected: Unknown task")
        mock_logging.info.assert_any_call(
            "Task 'Unknown task' - configuration dialog not implemented yet"
        )

    def test_event_filter_installation(self, qtbot: "QtBot") -> None:
        """Test that event filter is installed on status label."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # The event filter should be installed during update_status_icon
        # We can't directly test this, but we can verify the tooltip is cleared
        assert widget.status_label.toolTip() == ""

    def test_custom_tooltip_styling(self, qtbot: "QtBot") -> None:
        """Test custom tooltip has correct styling."""
        task = Task("Test task", False)
        widget = TaskItemWidget(task)
        qtbot.addWidget(widget)

        # Mock get_tooltip_text
        with patch.object(task, "get_tooltip_text", return_value="Test tooltip"):
            # Create a mock event
            mock_event = MagicMock()
            mock_pos = MagicMock()
            mock_pos.x.return_value = 100
            mock_pos.y.return_value = 200
            mock_event.globalPos.return_value = mock_pos

            widget.show_custom_tooltip(mock_event)

            assert widget.custom_tooltip is not None
            stylesheet = widget.custom_tooltip.styleSheet()
            assert "color: #333" in stylesheet
            assert "background-color: #f8f8f8" in stylesheet
            assert "border: 1px solid #ccc" in stylesheet
