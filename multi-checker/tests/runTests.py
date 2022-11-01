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
    info('Running {cmd} ...')
    res = run(cmd, onError='ignore')
    if res.exitcode != 0:
        fail(f'Command should succeed but failed with exit code {res.exitcode}: {cmd}')
    info('OK')

def expectFail(cmd: str):
    global testCount
    testCount = testCount + 1
    info('Running {cmd} ...')
    res = run(cmd, onError='ignore')
    if res.exitcode == 0:
        fail(f'Command should fail but succeded with exit code {res.exitcode}: {cmd}')
    info('OK')

wyppDir = '$HOME/devel/write-your-python-program/'

expectOk(f'python ../script/check.py --submission-dir python-wypp/ --kind python-wypp --wypp {wyppDir} 1')
expectOk(f'python ../script/check.py --kind python-wypp --wypp {wyppDir} 1')
expectFail(f'python ../script/check.py --submission-dir python-wypp/ --kind python-wypp --wypp {wyppDir} 2')
expectFail(f'python ../script/check.py --kind python-wypp --wypp {wyppDir} 2')

info(f'{testCount} tests were run successfully!')
