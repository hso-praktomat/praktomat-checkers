#!/usr/bin/env python3

# The tests are run with docker. You need to have docker running locally, and you need to pull
# the following image:
dockerImage = 'skogsbaer/praktomat-multi-checker:latest'

# Further, you need checkouts of the praktomat-tests and the praktomat-checkers repository under
# the following location:
praktomatTestsLocal = '$HOME/devel/praktomat-tests'
praktomatCheckersLocal = '$HOME/devel/praktomat-checkers'

runPythonTests = True
runHaskellTests = True
runJavaTests = True

from shell import *
import sys

useDocker = True

praktomatTestsDocker = '/praktomat-tests'
praktomatCheckersDocker = '/praktomat-checkers'

if useDocker:
    praktomatTests = praktomatTestsDocker
    praktomatCheckers = praktomatCheckersDocker
    thisDir = f'{praktomatCheckers}/multi-checker/tests'
else:
    praktomatTests = praktomatTestsLocal
    praktomatCheckers = praktomatCheckersLocal
    thisDir = '.'

checkScript = f'{praktomatCheckers}/multi-checker/script/check.py'

def fail(msg: str):
    print(msg)
    sys.exit(1)

def info(msg: str):
    print(f'[INFO] {msg}')

testCount = 0

def runCmd(cmd: str, onError='raise', capture=False):
    if useDocker:
        cmd = f'docker run --volume {praktomatCheckersLocal}:{praktomatCheckersDocker} '\
            f'--volume {praktomatTestsLocal}:{praktomatTestsDocker} '\
            f'--volume $HOME/devel/tick-trick-track:/external/tick-trick-track '\
            f'{dockerImage} {cmd}'
        info(cmd)
    return run(cmd, onError=onError, captureStderr=capture, captureStdout=capture,
               stderrToStdout=capture)

def expectOk(cmd: str):
    global testCount
    testCount = testCount + 1
    info(f'Running test, cmd: {cmd}')
    res = runCmd(cmd, onError='ignore')
    if res.exitcode != 0:
        fail(f'Command should succeed but failed with exit code {res.exitcode}: {cmd}')
    info('OK')

def expectFail(cmd: str, ecode=None):
    global testCount
    testCount = testCount + 1
    info(f'Running {cmd} ...')
    res = runCmd(cmd, onError='ignore')
    if res.exitcode == 0:
        fail(f'Command should fail but succeded with exit code {res.exitcode}: {cmd}')
    if ecode is not None:
        if res.exitcode != ecode:
            fail(f'Command should fail with exit code {ecode} but failed with {res.exitcode}: {cmd}')
        if res.exitcode == 1:
            # make sure there is no exception
            res2 = runCmd(cmd, onError='ignore', capture=True)
            if 'INTERNAL ERROR: checker raised an unexpected exception, this is a bug!' in res2.stdout:
                fail(f'Command raised an exception')
    info('OK')

def printHeader(title):
    print()
    delim = 80*'='
    print(delim)
    print(title)
    print(delim)
    print()

if runPythonTests:
    printHeader('Running Python Tests')

    wyppDir = '/wypp/' if useDocker else '$HOME/devel/write-your-python-program/'

    pythonTestDir = f'{praktomatTests}/python-prog1/'
    python2TestDir = f'{praktomatTests}/python-prog2/'
    localTestDir = f'{thisDir}/python-wypp'

    expectOk(f'python3 {checkScript} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 1')
    expectFail(f'python3 {checkScript} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 2', 121)
    expectFail(f'python3 {checkScript} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 2', 121)
    expectFail(f'python3 {checkScript} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 1,2', 121)
    expectFail(f'python3 {checkScript} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 3', 1)
    expectFail(f'python3 {checkScript} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 1,2,3', 1)

    pythonTests = [('solution-good', 0), ('solution-wrapped', 0), ('solution-partial', 121), ('solution-partial-missing', 121),
                ('solution-fail', 121), ('solution-error', 1), ('solution-with-own-test-errors', 1)]

    for d, ecode in pythonTests:
        cmd = f'python3 {checkScript} --test-dir {localTestDir} --submission-dir {localTestDir}/03/{d}/ python --wypp {wyppDir} --sheet 03'
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
    expectOk(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}10/solution python --wypp {wyppDir} --sheet 10')
    expectOk(f'python3 {checkScript} --test-dir {pythonTestDir} --submission-dir {pythonTestDir}10/solution/subdir python --wypp {wyppDir} --sheet 10')
    expectOk(f'python3 {checkScript} --test-dir {python2TestDir} --submission-dir {python2TestDir}P04-Listen/solution python --wypp {wyppDir} --sheet P04-Listen')

if runHaskellTests:
    printHeader('Running Haskell Tests')

    haskellTestDir = f'{praktomatTests}/haskell-advanced-prog'
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/02/solution/ --test-dir {haskellTestDir} haskell --sheet 02')

    expectFail(f'python3 {checkScript} --submission-dir {thisDir}/haskell/05-divide-by-zero/ --test-dir {haskellTestDir} haskell --sheet 05', 121)
    expectFail(f'python3 {checkScript} --submission-dir {haskellTestDir}/01/solution/ --test-dir {haskellTestDir} haskell --sheet 01', 121)
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/03/solution/ --test-dir {haskellTestDir} haskell --sheet 03')
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/04/solution/ --test-dir {haskellTestDir} haskell --sheet 04')
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/05/solution/ --test-dir {haskellTestDir} haskell --sheet 05')
    expectOk(f'python3 {checkScript} --submission-dir {haskellTestDir}/06/solution/ --test-dir {haskellTestDir} haskell --sheet 06')


if runJavaTests:
    printHeader('Running Java Tests')

    javaTestDir = f'{praktomatTests}/java-aud'
    checkstyle = '/opt/praktomat-addons/checkstyle.jar' if useDocker else './checkstyle-10.3.4-all.jar'
    localTestDir = f'{thisDir}/java-aud'

    expectOk(f'python3 {checkScript} --submission-dir {javaTestDir}/01-intro/solution --test-dir {javaTestDir} java --checkstyle {checkstyle} --sheet 01-intro')

    # Solution wrapped in another directory with failing tests
    expectFail(f'python3 {checkScript} --submission-dir {localTestDir}/passed-with-warnings/wrapper/ --test-dir {javaTestDir} java --checkstyle {checkstyle} --sheet 01-intro', 121)

    # Submission with BOM and iso encoding and with failing tests
    expectFail(f'python3 {checkScript} --submission-dir {localTestDir}/passed-with-warnings/AuD_Assignment_01/ --test-dir {javaTestDir} java --checkstyle {checkstyle} --sheet 01-intro', 121)

    # Submission with checkstyle errors
    expectFail(f'python3 {checkScript} --submission-dir {localTestDir}/fail/AuD_Assignment_01/ --test-dir {javaTestDir} java --checkstyle {checkstyle} --sheet 01-intro')

print()
info(f'{testCount} tests were run successfully!')
