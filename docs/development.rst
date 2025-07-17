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

* Then, from the root directory of this repository:
   * run ``uv pip install -e .`` to install dependencies into a virtual environment
   * run ``uv pip install -e ".[dev]"`` to install the development dependencies
   * run ``make test`` to run the test suite
   * run ``pre-commit install`` to install the pre-commit hooks
   * run ``make coverage`` to run unit tests and generate coverage report
