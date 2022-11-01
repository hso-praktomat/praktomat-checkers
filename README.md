# Praktomat Checkers with Docker

This repository contains checkers for praktomat when used with
[safe-docker](https://github.com/nomeata/safe-docker).
The checkers are independent from concrete tests for specific
courses. Such tests can be found, for example, [here](https://git.hs-offenburg.de/swehr/praktomat-tests).

## Checkers

At the moment, there are the following checkers:

* multi-checker: to be used with python and haskell submissions.
  * Python submission use [WYPP](https://github.com/skogsbaer/write-your-python-program).
    The checks make sure that the code loads successfully and that user-written tests
    pass. Currently, there is no support for external unit tests.

## How it works

Praktomat has the `ScriptChecker`, which simply runs a shell script
against the student submission. The exit code of this shell script
communicates the result of the checker back to praktomat.

The shell script runs either in the same environment as praktomat (same
machine or same docker container) or it runs inside an extra docker container.
[Safe-docker](https://github.com/nomeata/safe-docker) takes care of the
latter case.

When runing praktomat via docker (see
https://git.hs-offenburg.de/hbraun/praktomat-docker), you enable
execution inside an extra docker container by setting
the environment variable `PRAKTOMAT_CHECKER_IMAGE` to the docker
image the checker script should run in. Two more environment variables
are available for tweaking:

* `PRAKTOMAT_CHECKER_UID_MOD` prevents the UID and GID of the user
 executing the checks in the Docker container from being modified to match
 those of the user running Praktomat.
 Keep in mind that you might run your checkers as root (although it's just inside the container). It is determined by what you specify in your Dockerfile.
* `PRAKTOMAT_CHECKER_WRITABLE` can be used to make the filesystem of a
 container writable when running a checker. Otherwise, it's read-only.
 However, the directory containing the submission is always writable, regardless of this setting.

## How to write a new checker

* Subdirectory `checker-container` contains a dockerfile specifying a base
  image for the checkers in this repo.
* Write a new dockerfile that builds an image containing everything you
  need to run your checker script. You should use the base image
  from `checker-container` as the base of your new image.
* Write one ore more checker script. At the moment, you need for every
  phase (compilation, running student's tests, running instructor's tests)
  a different script, potentially also for different assignments. This
  script is uploaded to the task definition in praktomat and is executed
  for each submission in a docker container using the image specified
  in the preceding step. When the script is execute, the current
  working directory contains the file the student submitted, already in
  unzipped form.
