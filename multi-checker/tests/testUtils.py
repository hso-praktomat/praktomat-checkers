#!/usr/bin/env python3

from shell import *
import sys
import argparse

# The tests are run with docker. You need to have docker running locally, and you need to pull
# the following image:
dockerImage = 'skogsbaer/praktomat-multi-checker:latest'

# Further, you need checkouts of the praktomat-tests and the praktomat-checkers repository under
# the following location:
praktomatTestsLocal = expandEnvVars('$HOME/devel/praktomat-tests')
praktomatCheckersLocal = expandEnvVars('$HOME/devel/praktomat-checkers')

_DEBUG = False

thisDir = f'{praktomatCheckersLocal}/multi-checker/tests'

_praktomatCheckersDocker = '/praktomat-checkers'
checkScript = f'{_praktomatCheckersDocker}/multi-checker/script/check.py'

checkScriptArgs = ''
if _DEBUG:
    checkScriptArgs = "--debug"

def fail(msg: str):
    print(msg)
    sys.exit(1)

def info(msg: str):
    print(f'[INFO] {msg}')

def debug(msg: str):
    if _DEBUG:
        print(f'[DEBUG] {msg}')

def runCmd(cmd: str, onError='raise', capture=False, external=None, submissionDir=None, env=None):
    submissionDirDocker = '/submission'
    externalDirDocker = '/external'
    try:
        temp = mkTempDir(deleteAtExit=False)
        externalTmp = pjoin(temp, 'external')
        dirTmp = pjoin(temp, 'dir')
        workDirArg = ''
        submissionVolumeArg = ''
        if submissionDir is not None:
            debug(f'Copying {submissionDir} to {dirTmp}')
            cp(submissionDir, dirTmp)
            workDirArg = f'--workdir={submissionDirDocker}'
            submissionVolumeArg = f'--volume {dirTmp}:{submissionDirDocker}'
        if env:
            envStr = ' '.join([f'-e {k}="{v}"' for k,v in env.items()])
        else:
            envStr = ''
        cmdDocker = f'docker run {envStr} --rm ' \
            f'--volume {praktomatCheckersLocal}:{_praktomatCheckersDocker} '\
            f'--volume $HOME/devel/tick-trick-track:/external/tick-trick-track '\
            f'{submissionVolumeArg} {workDirArg} '
        if external is not None:
            cp(external, externalTmp)
            cmdDocker += f'--volume {externalTmp}:{externalDirDocker} '
        cmdDocker += f'{dockerImage} {cmd}'
        cmd = cmdDocker
        debug(cmd)
        return run(cmd, onError=onError, captureStderr=capture, captureStdout=capture,
                stderrToStdout=capture, env=env)
    finally:
        try:
            pass # rmdir(temp, recursive=True)
        except Exception:
            pass

def expectOk(cmd: str, external=None, submissionDir=None, env=None):
    print()
    info(f'Running test, cmd: {cmd}')
    capture = False if _DEBUG else True
    res = runCmd(cmd, onError='ignore', external=external, submissionDir=submissionDir, capture=capture, env=env)
    if res.exitcode != 0:
        print(res.stdout)
        fail(f'Command should succeed but failed with exit code {res.exitcode}: {cmd}')
    info('OK')
    return res

def expectFail(cmd: str, ecode=None, external=None, submissionDir=None, env=None):
    print()
    info(f'Running test, cmd: {cmd} ...')
    capture = False if _DEBUG else True
    res = runCmd(cmd, onError='ignore', external=external, submissionDir=submissionDir, capture=capture, env=env)
    if res.exitcode == 0:
        print(res.stdout)
        fail(f'Command should fail but succeded with exit code {res.exitcode}: {cmd}')
    if ecode is not None:
        if res.exitcode != ecode:
            print(res.stdout)
            fail(f'Command should fail with exit code {ecode} but failed with {res.exitcode}: {cmd}')
        if res.exitcode == 1:
            # make sure there is no exception
            res2 = runCmd(cmd, onError='ignore', external=external, capture=True, submissionDir=submissionDir, env=env)
            if 'INTERNAL ERROR: checker raised an unexpected exception, this is a bug!' in res2.stdout:
                print(res2.stdout)
                fail(f'Command raised an exception')
    info('OK')
    return res
