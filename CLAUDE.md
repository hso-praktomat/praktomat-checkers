See @README.md for the general behavior of this tool.

- This project uses static type checking for Python via pyright, configured in
  `pyproject.toml` under `[tool.pyright]` (strict mode). The type-checked code
  is `multi-checker/script/` and the test driver code in `multi-checker/tests/`
  (`testUtils.py`, `haskellTests.py`, `javaTests.py`, `pythonTests.py`).
- `multi-checker/tests/python-wypp/` is excluded from type checking: it
  contains checker test fixtures (sample student submissions) that import the
  external `wypp` package (not installed in this venv), and some of which are
  intentionally invalid Python.
- Python dependencies are declared in `requirements.txt` and installed with
  `pip` into the virtual environment at `.venv`.
- `multi-checker/check-ci` type checks the project (runs pyright inside the
  `.venv`).
- `multi-checker/tests/runTests` runs the checker's tests (needs the full
  java/gradle/stack/wypp toolchain plus Docker).
- Definition of done: `multi-checker/check-ci` must pass without errors.