Suggesting changes to the code
==============================

Suggestions for improvements are very welcome. Please use the
`GitHub issue tracker <https://github.com/hakonhagland/new-python-github-project/issues>`_ or submit
a pull request!

Pull request
------------

To set up an environment for developing and submitting a pull request, you could:

* Install pyenv
* Install the python versions listed in
  `.python_version <https://github.com/hakonhagland/new-python-github-project/blob/main/.python-version>`_ with pyenv
* Install uv:
   * On Linux and macOS: ``curl -LsSf https://astral.sh/uv/install.sh | sh``
   * On Windows (PowerShell): ``(Invoke-WebRequest -Uri https://astral.sh/uv/install.sh -UseBasicParsing).Content | sh``
   * Update your PATH to include uv's installation directory:
     * Linux/macOS: ``export PATH="$HOME/.cargo/bin:$PATH"``
     * Windows: Add ``%USERPROFILE%\.cargo\bin`` to your PATH
* On Windows, either:
   * `Install Chocolatey <https://chocolatey.org/install>`_ and run ``choco install make``
   * Or install `Git for Windows <https://git-scm.com/download/win>`_ and use Git Bash (which includes ``make``)
* Then, from the root directory of this repository:
   * run ``uv venv`` to create a virtual environment. If you are not able to install the exact Python versions
     listed in `.python_version`, you can use ``uv venv --python=<python-version>`` to specify a different Python
     interpreter.
   * run ```source .venv/bin/activate``` on Linux/macOS or ``.venv\Scripts\activate`` on Windows to activate
     the virtual environment. Note that by installing into a virtual environment the icons will not be installed
     correctly on Linux, but this might not be a problem if you are developing the application.
   * run ``uv sync`` or ``uv sync --python=<python-version>`` to install the dependencies
   * run ``pre-commit install --hook-type pre-commit`` and ``pre-commit install --hook-type commit-msg`` to install
     the pre-commit hooks
   * run ``make pre-commit`` to run the pre-commit hooks on all files
   * run ``make test`` to run the test suite
   * run ``make coverage`` to run unit tests and generate coverage report
