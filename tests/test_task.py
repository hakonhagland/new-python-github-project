"""Unit tests for task.py module."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QLabel

from new_python_github_project.task import ClickableLabel, PythonVersionDialog, Task

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


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
        from unittest.mock import patch

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
        from unittest.mock import patch

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
        from unittest.mock import patch

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
        from unittest.mock import patch

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
        from PyQt6.QtWidgets import QDialogButtonBox

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
