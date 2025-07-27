"""Unit tests for task.py module."""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QLabel

from new_python_github_project.task import ClickableLabel

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
