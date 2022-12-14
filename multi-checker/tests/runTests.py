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

def printHeader(title):
    print()
    delim = 80*'='
    print(delim)
    print(title)
    print(delim)
    print()

printHeader('Running Python Tests')

wyppDir = '$HOME/devel/write-your-python-program/'

expectOk(f'python3 ../script/check.py --submission-dir python-wypp/ python-wypp --wypp {wyppDir} --sheet 01 --assignment 1')
expectOk(f'python3 ../script/check.py python-wypp --wypp {wyppDir} --sheet 01 --assignment 1')
expectFail(f'python3 ../script/check.py --submission-dir python-wypp/ python-wypp --wypp {wyppDir} --sheet 01 --assignment 2')
expectFail(f'python3 ../script/check.py python-wypp --wypp {wyppDir} --sheet 01 --assignment 2')

printHeader('Running Haskell Tests')

haskellTestDir = '/Users/swehr/devel/praktomat-tests/haskell-advanced-prog'

expectFail(f'python3 ../script/check.py --submission-dir {haskellTestDir}/sheet-01/solution/ --test-dir {haskellTestDir} haskell --sheet 01', 121)
expectOk(f'python3 ../script/check.py --submission-dir {haskellTestDir}/sheet-02/solution/ --test-dir {haskellTestDir} haskell --sheet 02')
expectOk(f'python3 ../script/check.py --submission-dir {haskellTestDir}/sheet-03/solution/ --test-dir {haskellTestDir} haskell --sheet 03')
expectOk(f'python3 ../script/check.py --submission-dir {haskellTestDir}/sheet-04/solution/ --test-dir {haskellTestDir} haskell --sheet 04')
expectOk(f'python3 ../script/check.py --submission-dir {haskellTestDir}/sheet-05/solution/ --test-dir {haskellTestDir} haskell --sheet 05')
expectOk(f'python3 ../script/check.py --submission-dir {haskellTestDir}/sheet-06/solution/ --test-dir {haskellTestDir} haskell --sheet 06')
print()
info(f'{testCount} tests were run successfully!')
