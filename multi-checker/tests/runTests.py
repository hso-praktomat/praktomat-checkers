#!/usr/bin/env python3

from shell import *
import sys

runPythonTests = True
runHaskellTests = True

def fail(msg: str):
    print(msg)
    sys.exit(1)

def info(msg: str):
    print(f'[INFO] {msg}')

testCount = 0

def expectOk(cmd: str):
    global testCount
    testCount = testCount + 1
    info(f'Running test, cmd: {cmd}')
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

checkScript = '../script/check.py'

if runPythonTests:
    printHeader('Running Python Tests')

    wyppDir = '$HOME/devel/write-your-python-program/'
    pythonTestDir = '$HOME/devel/praktomat-tests/python-prog1/'
    python2TestDir = '$HOME/devel/praktomat-tests/python-prog2/'

    expectOk(f'python3 {checkScript} --submission-dir python-wypp/ python --wypp {wyppDir} --sheet 01 --assignment 1')
    expectOk(f'python3 {checkScript} python --wypp {wyppDir} --sheet 01 --assignment 1')
    expectFail(f'python3 {checkScript} --submission-dir python-wypp/ python --wypp {wyppDir} --sheet 01 --assignment 2')
    expectFail(f'python3 {checkScript} python --wypp {wyppDir} --sheet 01 --assignment 2')

    pythonTests = [('solution-good', 0), ('solution-partial', 121), ('solution-partial-missing', 121),
                ('solution-fail', 121), ('solution-error', 1)]

    for d, ecode in pythonTests:
        cmd = f'python3 {checkScript} --test-dir python-wypp/ --submission-dir python-wypp/03/{d}/ python --wypp {wyppDir} --sheet 03'
        if ecode == 0:
            expectOk(cmd)
        else:
            expectFail(cmd, ecode)

    expectOk(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}/09/solution/ python --wypp {wyppDir} --sheet 09')

    expectOk(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}/labortest_2/solution/ python --wypp {wyppDir} --sheet labortest_2')
    expectFail(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}/labortest_2/solution-partial/ python --wypp {wyppDir} --sheet labortest_2', 121)
    expectFail(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}/labortest_2/solution-nofiles/ python --wypp {wyppDir} --sheet labortest_2', 1)

    expectFail(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}abschlussprojekt/solution-fail python --wypp {wyppDir} --sheet abschlussprojekt')
    expectFail(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}abschlussprojekt/solution-simple python --wypp {wyppDir} --sheet abschlussprojekt', 121)
    expectOk(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}abschlussprojekt/solution python --wypp {wyppDir} --sheet abschlussprojekt')
    expectOk(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}10/solution python --sheet 10')
    expectOk(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}10/solution/subdir python --sheet 10')

    expectOk(f'python3 {checkScript} --test-dir {python2TestDir} --submission-dir {python2TestDir}P04-Listen/solution python --sheet P04-Listen')

if runHaskellTests:
    printHeader('Running Haskell Tests')

    haskellTestDir = '$HOME/devel/praktomat-tests/haskell-advanced-prog'
    expectFail(f'python3 {checkScript} --submission-dir haskell/05-divide-by-zero/ --test-dir {haskellTestDir} haskell --sheet 05', 121)

    expectFail(f'python3 {checkScript} --submission-dir {haskellTestDir}/01/solution/ --test-dir {haskellTestDir} haskell --sheet 01', 121)
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/02/solution/ --test-dir {haskellTestDir} haskell --sheet 02')
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/03/solution/ --test-dir {haskellTestDir} haskell --sheet 03')
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/04/solution/ --test-dir {haskellTestDir} haskell --sheet 04')
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/05/solution/ --test-dir {haskellTestDir} haskell --sheet 05')
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/06/solution/ --test-dir {haskellTestDir} haskell --sheet 06')
    print()
    info(f'{testCount} tests were run successfully!')
