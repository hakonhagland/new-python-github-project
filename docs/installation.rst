Installation
============

To install the application, ensure that you have Python version 3.11 or higher.

From PyPI
---------

.. code-block:: bash

    $ pip install --user new-python-gh-project

.. note::
    The ``--user`` flag is used to install the application in the user's home directory.
    This is a good practice to avoid conflicts with system-wide installations. It is possible
    to install into a virtual environment and avoid the ``--user`` flag, but then the application
    icons will not be installed correctly on Linux.

From GitHub
-----------

* Download the git source:

.. code-block:: bash

    $ git clone --depth=1 https://github.com/hakonhagland/new-python-gh-project.git
    $ cd new-python-gh-project
    $ pip install --user .

.. note::
    For development installation from GitHub see: :doc:`Development <development>`

* Run the application to verify that the installation was successful:

.. code-block:: bash

    $ new-python-gh-project
