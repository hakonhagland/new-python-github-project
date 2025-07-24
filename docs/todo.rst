================
TODO and Roadmap
================

This document tracks known issues, planned enhancements, and future development goals for the New Python GitHub Project application.

Known Issues
============

macOS CMD+Tab Generic Icon
---------------------------

**Status**: Open

**Description**: 
On macOS, when using CMD+Tab to switch between applications, the New Python GitHub Project app displays a generic Python icon instead of the custom application icon.

**Root Cause**:
This is a macOS limitation when running Python applications directly as scripts rather than as proper macOS application bundles (.app). The issue occurs because:

1. **Process Identity**: macOS identifies the running process as the Python interpreter, not as the specific application
2. **Bundle Structure**: Python scripts lack the proper ``.app`` bundle structure that macOS uses for application metadata
3. **Icon Association**: The dock and CMD+Tab switcher rely on bundle information (``Info.plist``) to determine the correct icon

**Current Behavior**:
- ✅ **Menu bar**: Shows correct name "New Python GitHub Project" (fixed via PyObjC)
- ✅ **Window icon**: Shows correct custom icon
- ❌ **CMD+Tab**: Shows generic Python icon
- ❌ **Dock**: Shows generic Python icon when app is running

**Potential Solutions**:

1. **Application Bundling** (Recommended)
   - Use tools like ``py2app`` or ``briefcase`` to create proper macOS app bundles
   - Provides native macOS integration with proper icon handling
   - **Pros**: Complete solution, professional distribution
   - **Cons**: Adds build complexity, larger distribution size

2. **Runtime Bundle Modification**
   - Dynamically modify the NSBundle at runtime to set more metadata
   - Extend current PyObjC solution beyond just CFBundleName
   - **Pros**: No build changes required
   - **Cons**: Limited effectiveness, may not work for dock integration

3. **Custom Launcher Script**
   - Create a native macOS launcher that spawns the Python application
   - Use AppleScript or native code to set proper application identity
   - **Pros**: Maintains current Python-based architecture
   - **Cons**: Complex implementation, potential maintenance overhead

**Priority**: Low (cosmetic issue, doesn't affect functionality)

**Related Files**:
- ``src/new_python_github_project/helpers.py:545`` (``_fix_macos_app_name`` function)
- ``pyproject.toml`` (PyObjC dependency configuration)

Future Enhancements
===================

GUI Improvements
----------------

1. **Theme Support**
   - Add dark/light theme toggle
   - Respect system theme preferences
   - Custom color schemes

2. **Window Management**  
   - Remember window size and position
   - Multiple project windows support
   - Tabbed interface for multiple projects

3. **Progress Indicators**
   - Real-time progress bars for long operations
   - Background task status
   - Cancel operation support

Development Tools Integration
-----------------------------

1. **IDE Integration**
   - VS Code project setup templates
   - PyCharm configuration files
   - Sublime Text project files

2. **CI/CD Templates**
   - GitHub Actions workflow templates
   - GitLab CI configuration
   - Pre-commit hook templates

3. **Documentation Generation**
   - Auto-generate API documentation structure
   - README template customization
   - Sphinx configuration options

Platform Support
-----------------

1. **Windows Improvements**
   - Windows-specific icon handling verification
   - PowerShell script templates
   - Windows Subsystem for Linux (WSL) support

2. **Linux Desktop Integration**
   - .desktop file generation verification
   - Wayland compatibility testing
   - Flatpak/Snap package support

3. **Cross-Platform Testing**
   - Automated testing on all platforms
   - Virtual machine test environments
   - Container-based testing

Configuration Management
------------------------

1. **Project Templates**
   - Customizable project templates
   - Template marketplace/sharing
   - Version control for templates

2. **Settings Profiles**
   - Multiple configuration profiles
   - Import/export settings
   - Team configuration sharing

3. **Plugin System**
   - Plugin architecture design
   - Third-party extension support
   - API for custom integrations

Completed Items
===============

✅ **macOS Menu Bar Name Fix** (v0.1.0)
   - Fixed menu bar showing "python3" instead of application name
   - Implemented PyObjC-based solution with CFBundleName modification
   - Added proper environment inheritance for subprocess detachment

✅ **Icon Loading System** (v0.1.0)
   - Implemented hierarchical icon loading with fallback system
   - Added cross-platform icon theme support
   - Proper virtual environment icon path resolution

✅ **Environment Isolation** (v0.1.0)
   - Fixed subprocess environment inheritance issues
   - Ensured virtual environment preservation in detached processes
   - Added proper dependency management with uv

Contributing
============

If you'd like to work on any of these items:

1. Check the `GitHub Issues <https://github.com/hakonhagland/new-python-github-project/issues>`_ for existing discussions
2. Create a new issue to discuss your proposed changes
3. Follow the development guidelines in the development documentation
4. Submit a pull request with your implementation

Priority levels:
- **High**: Critical functionality, major bugs
- **Medium**: Important features, minor bugs  
- **Low**: Nice-to-have features, cosmetic issues