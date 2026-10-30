# CLAUDE.md

Checkers for [Praktomat](https://github.com/hso-praktomat/praktomat-docker) that run in Docker.
The only checker is `multi-checker`, a Python script that grades student submissions in Python
(WYPP or unittest), Haskell (stack) and Java (Gradle + Checkstyle). It also has an `llm-tutor`
command that passes a submission to the LLM tutor. See @README.md for the general behavior of
this tool.

## Definition of done

A change is done only when both checks pass on the final state of the code:

1. **Type check is clean.** Pyright reports `0 errors, 0 warnings` (commands below). Don't get
   there with `# type: ignore` / `# pyright: ignore`, casts to `Any` or a looser
   `[tool.pyright]` config. Fix the types instead.
2. **The whole test suite passes.** `./runTests` in `multi-checker/tests` (no `-k`, nothing
   skipped or deselected) finishes with every test passing.

If you can't run one of the two checks, the change isn't done. Say which check you couldn't run
and why, and leave that run to the user. Never report a change as finished because the type check alone passed.

Bug fixes are test-first: add a test that reproduces the bug, show that it fails, then fix the
bug and show that the test passes. New behaviour gets a new `test_…` function in the matching
`multi-checker/tests/*Tests.py`.

## Type check

Run `multi-checker/check-ci`. Pyright runs in strict mode, configured under `[tool.pyright]` in
`pyproject.toml`. It checks `multi-checker/script/` and the test driver code in
`multi-checker/tests/` (`testUtils.py`, `haskellTests.py`, `javaTests.py`, `pythonTests.py`,
`i18nTests.py`).
`multi-checker/tests/python-wypp/` is excluded: it holds sample student submissions that import
the external `wypp` package (not installed in the venv), and some of them are intentionally
invalid Python.

`check-ci` picks the venv by OS:

- Linux (devcontainer, CI, Docker): `.venv_linux`. The devcontainer's `postCreateCommand`
  creates it with uv from the image's Python (3.14). CI creates it with Python 3.14 from
  `requirements.txt`.
- macOS host: `.venv`.

Both venvs live in the same checkout because the devcontainer bind-mounts it. Never use or
recreate `.venv` from Linux: it is the host's macOS venv, and its interpreter symlinks point to
`/Users/...`. `pyproject.toml` deliberately names no venv, because a `venv` setting there would
override the `--pythonpath` that `check-ci` passes. So run pyright only through `check-ci`; a
bare `pyright` reports `shell` and `yaml` as unresolved.

Strict mode needs libpyshell 0.6.0 or newer, the first version that ships type information.
With 0.5.0, pyright reports `Stub file not found for "shell"`. `requirements.txt` doesn't pin
pyright. CI uses the latest release, so CI's result is the one that counts.

## Tests

There are only integration tests. Each test runs `check.py` against a sample submission and
checks the exit code (sometimes also the output). The tests run in one of two modes:

- **Docker** (the default, e.g. on the macOS host): `check.py` runs inside the image
  `skogsbaer/praktomat-multi-checker:latest` built from `multi-checker/docker/`.
- **Local** (`PRAKTOMAT_TESTS_LOCAL=1`, set by the devcontainer): `check.py` runs directly in the
  devcontainer. Its image `skogsbaer-devimage` provides the tools of the Docker image under the
  same paths and versions, and the devcontainer mounts the rest.

```sh
cd multi-checker/tests
./runTests                    # full suite: pytest --verbose haskellTests.py javaTests.py pythonTests.py i18nTests.py
./runTests -k test_java02     # a single test, while iterating
./runTests --capture=no ...   # show the checker's output
```

On the host, `./run-tests-on-host` (in the repo root) builds the image from the local Dockerfiles
(`docker-build --build-base --no-push`) and runs the whole suite in Docker mode. Its arguments go
to `runTests`. The devcontainer has no Docker: if a change touches the Dockerfiles, ask the user
to run `./run-tests-on-host` on the host.

Prerequisites, hard-coded in `testUtils.py` and the test files:

- `pytest` and `libpyshell` (`testUtils.py` does `from shell import *`). On Linux, `runTests`
  takes them from `.venv_linux`; on the Mac from `.venv` if it contains pytest, otherwise it
  uses the `pytest` on `PATH`.
- A checkout of praktomat-tests at `/praktomat-tests` (the devcontainer mounts
  `~/devel/praktomat-tests` there), otherwise at `$HOME/devel/praktomat-tests`. It holds most
  fixtures; only a few are in `multi-checker/tests/{python-wypp,java-aud,haskell}`.
- **This repo at `$HOME/devel/praktomat-checkers`, or else at `/work` (the devcontainer).**
  The tests mount *that* path into the container and run *its* `check.py` and fixtures, not
  those of the checkout you are in. Run from another clone or a git worktree and you test the
  wrong code.
- Docker mode: Docker running with the image present, and a checkout of
  github.com/skogsbaer/tick-trick-track at `$HOME/devel/tick-trick-track`. The tests mount it
  at `/external/tick-trick-track`; `test_python12`–`14` need it.
- Local mode: the devcontainer provides WYPP at `/wypp` (mount of
  `~/devel/write-your-python-program`, at least version 2.5.2: the checker relies on its exit codes for
  `--check`), tick-trick-track at `/external/tick-trick-track` (mount
  of `~/devel/tick-trick-track`), Checkstyle at `/opt/praktomat-addons/checkstyle.jar`, Java 27
  (`JAVA_HOME=/opt/jdk-27`), Gradle 9.8.2 with its dependency cache in `/root/.gradle`, the
  Haskell packages in the `lts-24.3` snapshot, and `python3` (3.14) with pyyaml, libpyshell,
  aiofiles, aiohttp, ruff and pylint (same versions as in the Dockerfile), and the locales
  `en_US.UTF-8` and `de_DE.UTF-8`.

What a test run picks up:

- Edits under `multi-checker/script/` take effect immediately in both modes. Docker mode mounts
  the script into the container.
- Edits to `multi-checker/docker/` or `checker-container/` (toolchains, pinned WYPP and
  llm-tutor commits, Python packages) take effect in Docker mode only after the image is
  rebuilt, which `./run-tests-on-host` does. Local mode never sees them. **Always pass
  `--no-push` to `multi-checker/docker/docker-build` unless the user asks for a push:** without
  it, the script pushes images for `linux/amd64` (the default platform) to Docker Hub.
- **Keep the Docker image and the devcontainer image in sync.** If you change a tool or its
  version in the Dockerfiles, `skogsbaer-devimage` needs the same change. It is built outside
  this repo, so tell the user. Known difference: local mode uses the WYPP checkout on the host
  instead of the pinned commit.

The `llm-tutor` command has no tests (its fixtures were removed in 883483b). If you change
`llm_tutor.py`, add a test (e.g. using `--fake-llm`) or tell the user that the change is untested.

## Layout

- `multi-checker/script/`: the checker. It is copied into the image as `/checker` and started
  as `python3 /checker/check.py <python|python-style|haskell|java|llm-tutor> ...`.
  - `check.py` parses the arguments and dispatches to `python.py`, `pythonStyle.py`,
    `haskell.py`, `java.py` or `llm_tutor.py`.
  - `exercise.py` parses each sheet's `exercise.yaml` (assignments, points, test files).
    `testContext.py` collects the results, prints the report and exits.
  - `common.py` and `utils.py` hold shared helpers (`runWithTimeout`, `findSolutionDir`,
    `abort`, `bug`, …).
  - `build.gradle.kts` and `checkstyle.xml` are the defaults for Java submissions.
  - `i18n.py` selects the language of the messages (English or German) like WYPP: option
    `--lang en|de`, otherwise the locale, otherwise English. It is passed on to WYPP. The image
    sets `LANG=de_DE.UTF-8` (in `checker-container/`), the devcontainer `LC_ALL=C.utf8`, so the
    default language differs between Docker and local mode. The tests therefore pass `--lang en`
    in `checkScriptArgs`; tests of the language use `checkScriptArgsNoLang` and `localeEnv`.
  - `pythonStyle.py` checks the coding conventions of Python submissions with ruff (layout, type
    annotations) and pylint (naming), configured in `python-style/`. Violations give exit
    code `1`. In messages, say "coding conventions" (German "Programmierkonventionen"), not
    "coding style". The fixtures of its tests are in `multi-checker/tests/python-wypp/style/`.
- `multi-checker/docker/`: the image with stack/GHC, JDK + Gradle, WYPP and llm-tutor, built on
  `checker-container/` (Ubuntu noble base plus Checkstyle).
- `multi-checker/task-templates/`: a Praktomat task template that calls the checker.

## Conventions

- **Exit codes are the contract with Praktomat:** `0` means everything is OK. `121`
  (`OK_WITH_WARNINGS_EXIT_CODE`) means the code compiled/loaded but some tests failed or files
  are missing. `1` means compile/load failure, configuration error or internal error. The tests
  assert exact codes and check that a `1` never comes from an uncaught exception.
- Call `abort(msg)` for problems with the submission or the task configuration (it prints
  `ERROR: …`, in German `FEHLER: …`) and `bug(msg)` for internal errors. stdout is the checker
  report shown in Praktomat, so keep it readable for students.
- Pass every message for students and instructors through `tr` from `i18n.py`, with the English
  text as key and placeholders for values (`tr('File {file} not found', file=p)`, no f-strings),
  and add the German translation to `DE`. Messages built before the language is known are marked
  with `trKey` and translated with `tr` when shown. `test_translations_complete` checks that
  every key has a translation. Messages of `bug` stay English.
- The image, the devcontainer and CI run Python 3.14, but pyright checks against Python 3.10
  (`pythonVersion` in `pyproject.toml`), so code must stay 3.10-compatible.
- Use camelCase for functions, variables and parameters. `llm_tutor.py` doesn't; don't copy
  it. Modules use `from shell import *` (libpyshell: `run`, `pjoin`, `isFile`, `ls`, …) and
  `from utils import *`. Prefer those helpers over `subprocess` and `os.path`.
- New runtime dependencies go into `multi-checker/docker/Dockerfile` (pinned) *and* into
  `requirements.txt` (for the type check). The image pins `libPyshell==0.5.0` while
  `requirements.txt` installs the latest version, so stick to the API of the image's version.
