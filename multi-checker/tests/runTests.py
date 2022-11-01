#!/usr/bin/env python3

from shell import *
import sys

def fail(msg: str):
    print(msg)
    sys.exit(1)

def info(msg: str):
    print(f'[INFO] {msg}')

testCount = 0

def expectOk(cmd: str):
    global testCount
    testCount = testCount + 1
    info(f'Running {cmd} ...')
    res = run(cmd, onError='ignore')
    if res.exitcode != 0:
        fail(f'Command should succeed but failed with exit code {res.exitcode}: {cmd}')
    info('OK')

def expectFail(cmd: str, ecode=None):
    global testCount
    testCount = testCount + 1
    info(f'Running {cmd} ...')
    res = run(cmd, onError='ignore')
    if res.exitcode == 0:
        fail(f'Command should fail but succeded with exit code {res.exitcode}: {cmd}')
    if ecode is not None:
        if res.exitcode != ecode:
            fail(f'Command should fail with exit code {ecode} but failed with {res.exitcode}: {cmd}')
    info('OK')

wyppDir = '$HOME/devel/write-your-python-program/'

expectOk(f'python3 ../script/check.py --submission-dir python-wypp/ python-wypp --wypp {wyppDir} --assignment 1')
expectOk(f'python3 ../script/check.py python-wypp --wypp {wyppDir} --assignment 1')
expectFail(f'python3 ../script/check.py --submission-dir python-wypp/ python-wypp --wypp {wyppDir} --assignment 2')
expectFail(f'python3 ../script/check.py python-wypp --wypp {wyppDir} --assignment 2')

haskellTestDir = '/Users/swehr/devel/praktomat-tests/haskell-advanced-prog'

expectFail(f'python3 ../script/check.py --submission-dir {haskellTestDir}/ex01/solution/ --test-dir {haskellTestDir} haskell --sheet 01', 121)
print()
info(f'{testCount} tests were run successfully!')
