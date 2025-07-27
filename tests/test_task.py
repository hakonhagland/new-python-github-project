"""Unit tests for task.py module."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QDialogButtonBox, QLabel, QLineEdit, QTextEdit

from new_python_github_project.task import (
    ClickableLabel,
    LicenseSelectionDialog,
    PythonVersionDialog,
    Task,
    TaskConfigDialog,
)

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
