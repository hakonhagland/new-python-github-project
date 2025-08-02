#!/bin/bash
# Cross-platform coverage script for PyQt6 testing
# Windows: GUI windows shown during tests (QT_QPA_PLATFORM=offscreen causes crashes)
# Unix/Linux/macOS: Headless testing with offscreen platform

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OS" == "Windows_NT" ]]; then
    coverage run -m pytest tests
else
    QT_QPA_PLATFORM=offscreen coverage run -m pytest tests
fi
