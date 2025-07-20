Debugging the Daemonized Application
=====================================

Since the application forks twice and detaches from the terminal, traditional debugging methods like ``breakpoint()`` don't work. Here are the recommended approaches:

File-based Debugging
--------------------

Use the ``debug_to_file()`` function to write debug information to a file:

.. code-block:: python

    from new_python_github_project.helpers import debug_to_file

    # Simple debug message
    debug_to_file("Application started")

    # Debug with data
    debug_to_file("User clicked button", {"button": "create", "timestamp": "2024-01-01"})

The debug file is written to ``/tmp/pyqt_debug.log`` by default. You can monitor it with:

.. code-block:: bash

    tail -f /tmp/pyqt_debug.log

Remote Debugging with debugpy
-----------------------------

For advanced debugging with breakpoints, use remote debugging:

1. **Setup remote debugging before daemonizing:**

   .. code-block:: python

       from new_python_github_project.helpers import setup_remote_debugging

       # Call this before daemonizing
       setup_remote_debugging(host="localhost", port=5678)
       daemonize(config, verbose)

2. **Connect your debugger:**

   - **VS Code**: Add to ``.vscode/launch.json``:

     .. code-block:: json

         {
             "name": "Python: Remote Attach",
             "type": "python",
             "request": "attach",
             "connect": {
                 "host": "localhost",
                 "port": 5678
             }
         }

   - **PyCharm**: Go to Run → Edit Configurations → + → Python Debug Server

   - **Command line**: Use ``debugpy`` directly:

     .. code-block:: bash

         python -m debugpy --listen localhost:5678 --wait-for-client your_script.py

3. **Set breakpoints in your code:**

   .. code-block:: python

       import debugpy

       # Your breakpoint will work now
       breakpoint()  # This will pause execution and wait for debugger

       # Or use debugpy.wait_for_client() to wait for debugger connection
       debugpy.wait_for_client()

Logging-based Debugging
-----------------------

The application already has comprehensive logging. Enable verbose logging:

.. code-block:: python

    import logging
    logging.basicConfig(level=logging.DEBUG)

Or check the application's log file (configured in your config).

Signal-based Debugging
----------------------

You can also use signals to trigger debugging:

.. code-block:: python

    import signal
    import sys

    def debug_handler(signum, frame):
        debug_to_file("Received debug signal", {"signal": signum})
        # You can also dump stack traces here

    signal.signal(signal.SIGUSR1, debug_handler)

Then trigger debugging with:

.. code-block:: bash

    kill -USR1 PID

Best Practices
--------------

1. **Use file-based debugging for quick checks**
2. **Use remote debugging for complex debugging sessions**
3. **Always include process IDs in debug messages**
4. **Use structured logging with JSON data**
5. **Monitor debug files in real-time with ``tail -f``**

Example Usage
-------------

.. code-block:: python

    from new_python_github_project.helpers import debug_to_file, setup_remote_debugging

    # Setup remote debugging (optional)
    setup_remote_debugging()

    # Your application code
    def handle_button_click():
        debug_to_file("Button clicked", {"button": "create_project"})

        try:
            # Your logic here
            result = create_project()
            debug_to_file("Project created successfully", {"result": result})
        except Exception as e:
            debug_to_file("Error creating project", {"error": str(e), "type": type(e).__name__})
            raise
