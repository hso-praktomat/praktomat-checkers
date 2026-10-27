# CLAUDE.md

Checkers for [Praktomat](https://github.com/hso-praktomat/praktomat-docker) that run in Docker.
The only checker is `multi-checker`, a Python script that grades student submissions in Python
(WYPP or unittest), Haskell (stack) and Java (Gradle + Checkstyle). It also has an `llm-tutor`
command that passes a submission to the LLM tutor. README.md explains how Praktomat invokes it.

## Definition of done

A change is done only when both checks pass on the final state of the code:

1. **Type check is clean.** Pyright reports `0 errors, 0 warnings` (commands below). Don't get
   there with `# type: ignore` / `# pyright: ignore`, casts to `Any` or a looser
   `pyrightconfig.json`. Fix the types instead.
2. **The whole test suite passes.** `./runTests` in `multi-checker/tests` (no `-k`, nothing
   skipped or deselected) finishes with every test passing.

If you can't run one of the two checks, the change isn't done. The devcontainer has no Docker,
so the tests can't run there. Say which check you couldn't run and why, and leave that run to
the user. Never report a change as finished because the type check alone passed.

Bug fixes are test-first: add a test that reproduces the bug, show that it fails, then fix the
bug and show that the test passes. New behaviour gets a new `test_…` function in the matching
`multi-checker/tests/*Tests.py`.

## Type check

Pyright checks `multi-checker/script/*.py`; `multi-checker/tests` is excluded in
`pyrightconfig.json`. Run it from the repo root:

- On the host (macOS) and in CI: `multi-checker/check-ci`. It runs `.venv/bin/pyright`; CI
  builds `.venv` from `requirements.txt` with Python 3.12.
- In the devcontainer: `uvx pyright`. `/work/.venv` is the host's macOS venv, bind-mounted, and
  its interpreter symlinks point to `/Users/...`, so `check-ci` fails with `bad interpreter`.
  Pyright still finds `shell` and `yaml` in `.venv/lib/python3.12/site-packages`. Don't delete
  or recreate `.venv`; it belongs to the host.

`requirements.txt` doesn't pin pyright. CI uses the latest release, so CI's result is the one
that counts.

## Tests

There are only integration tests. Each test runs `check.py` inside the Docker image against a
sample submission and checks the exit code (sometimes also the output).

```sh
cd multi-checker/tests
./runTests                    # full suite: pytest --verbose haskellTests.py javaTests.py pythonTests.py
./runTests -k test_java02     # a single test, while iterating
./runTests --capture=no ...   # show the checker's output
```

Prerequisites, hard-coded in `testUtils.py`:

- Docker running, with image `skogsbaer/praktomat-multi-checker:latest` present.
- `pytest` and `libpyshell` importable by the `pytest` on `PATH` (`testUtils.py` does
  `from shell import *`).
- A checkout of praktomat-tests at `$HOME/devel/praktomat-tests`. It holds most fixtures; only
  a few are in `multi-checker/tests/{python-wypp,java-aud,haskell}`.
- **This repo at `$HOME/devel/praktomat-checkers`.** The tests mount *that* path into the
  container and run *its* `check.py` and fixtures, not those of the checkout you are in. Run
  from another clone or a git worktree and you test the wrong code.

What a test run picks up:

- Edits under `multi-checker/script/` take effect immediately, because the script is mounted.
- Edits to `multi-checker/docker/` or `checker-container/` (toolchains, pinned WYPP and
  llm-tutor commits, Python packages) take effect only after you rebuild the image with
  `multi-checker/docker/docker-build [--build-base] linux/arm64`. **Run `docker-build` without
  `linux/arm64` only if the user asks:** with the default platform `linux/amd64` it pushes the
  image to Docker Hub.

The `llm-tutor` command has no tests (its fixtures were removed in 883483b). If you change
`llm_tutor.py`, add a test (e.g. using `--fake-llm`) or tell the user that the change is untested.

## Layout

- `multi-checker/script/`: the checker. It is copied into the image as `/checker` and started
  as `python3 /checker/check.py <python|haskell|java|llm-tutor> ...`.
  - `check.py` parses the arguments and dispatches to `python.py`, `haskell.py`, `java.py` or
    `llm_tutor.py`.
  - `exercise.py` parses each sheet's `exercise.yaml` (assignments, points, test files).
    `testContext.py` collects the results, prints the report and exits.
  - `common.py` and `utils.py` hold shared helpers (`runWithTimeout`, `findSolutionDir`,
    `abort`, `bug`, …).
  - `build.gradle.kts` and `checkstyle.xml` are the defaults for Java submissions.
- `multi-checker/docker/`: the image with stack/GHC, JDK + Gradle, WYPP and llm-tutor, built on
  `checker-container/` (Ubuntu noble base plus Checkstyle).
- `multi-checker/task-templates/`: a Praktomat task template that calls the checker.

## Conventions

- **Exit codes are the contract with Praktomat:** `0` means everything is OK. `121`
  (`OK_WITH_WARNINGS_EXIT_CODE`) means the code compiled/loaded but some tests failed or files
  are missing. `1` means compile/load failure, configuration error or internal error. The tests
  assert exact codes and check that a `1` never comes from an uncaught exception.
- Call `abort(msg)` for problems with the submission or the task configuration (it prints
  `FEHLER: …`) and `bug(msg)` for internal errors. stdout is the checker report shown in
  Praktomat, so keep it readable for students.
- Python 3.12 (image and CI). Don't use features from newer versions.
- Use camelCase for functions, variables and parameters. `llm_tutor.py` doesn't; don't copy
  it. Modules use `from shell import *` (libpyshell: `run`, `pjoin`, `isFile`, `ls`, …) and
  `from utils import *`. Prefer those helpers over `subprocess` and `os.path`.
- New runtime dependencies go into `multi-checker/docker/Dockerfile` (pinned) *and* into
  `requirements.txt` (for the type check). The image pins `libPyshell==0.5.0` while
  `requirements.txt` installs the latest version, so stick to the API of the image's version.
