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

runPythonTests = True
runHaskellTests = True
runJavaTests = True
useDocker = True
_DEBUG = False

def parseArgs():
    parser = argparse.ArgumentParser(description="Run tests")
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('--haskell-only', action='store_true', help="Enable only Haskell processing")
    parser.add_argument('--python-only', action='store_true', help="Enable only Python processing")
    parser.add_argument('--java-only', action='store_true', help="Enable only Java processing")
    return parser.parse_args()

args = parseArgs()
if args.debug:
    _DEBUG = True
if args.haskell_only:
    runPythonTests = False
    runJavaTests = False
if args.python_only:
    runHaskellTests = False
    runJavaTests = False
if args.java_only:
    runPythonTests = False
    runHaskellTests = False

praktomatTestsDocker = '/praktomat-tests'
praktomatCheckersDocker = '/praktomat-checkers'
sheetDirDocker = '/external'

if useDocker:
    praktomatTests = praktomatTestsDocker
    praktomatCheckers = praktomatCheckersDocker
    thisDir = f'{praktomatCheckers}/multi-checker/tests'
else:
    praktomatTests = praktomatTestsLocal
    praktomatCheckers = praktomatCheckersLocal
    thisDir = '.'

checkScript = f'{praktomatCheckers}/multi-checker/script/check.py'
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

testCount = 0

def runCmd(cmd: str, onError='raise', capture=False, external=None, dir=None, env=None):
    try:
        externalTmp = mkTempDir(deleteAtExit=False)
        if useDocker:
            workDirArg = ""
            if dir is not None:
                workDirArg = f'--workdir={dir}'
            if env:
                envStr = ' '.join([f'-e {k}="{v}"' for k,v in env.items()])
            else:
                envStr = ''
            cmdDocker = f'docker run {envStr} --rm --volume {praktomatCheckersLocal}:{praktomatCheckersDocker} '\
                f'--volume {praktomatTestsLocal}:{praktomatTestsDocker} '\
                f'--volume $HOME/devel/tick-trick-track:/external/tick-trick-track '\
                f'{workDirArg} '
            if external is not None:
                cp(external, externalTmp) # copies external to externalTmp (as a subdir)
                cmdDocker += f'--volume {pjoin(externalTmp, basename(external))}:{sheetDirDocker} '
            cmdDocker += f'{dockerImage} {cmd}'
            cmd = cmdDocker
        debug(cmd)
        return run(cmd, onError=onError, captureStderr=capture, captureStdout=capture,
                stderrToStdout=capture, env=env)
    finally:
        try:
            rmdir(externalTmp, recursive=True)
        except Exception:
            pass

def expectOk(cmd: str, external=None, dir=None, env=None):
    global testCount
    testCount = testCount + 1
    print()
    info(f'Running test, cmd: {cmd}')
    capture = False if _DEBUG else True
    res = runCmd(cmd, onError='ignore', external=external, dir=dir, capture=capture, env=env)
    if res.exitcode != 0:
        print(res.stdout)
        fail(f'Command should succeed but failed with exit code {res.exitcode}: {cmd}')
    info('OK')
    return res

def expectFail(cmd: str, ecode=None, external=None, dir=None, env=None):
    global testCount
    testCount = testCount + 1
    print()
    info(f'Running test, cmd: {cmd} ...')
    capture = False if _DEBUG else True
    res = runCmd(cmd, onError='ignore', external=external, dir=dir, capture=capture, env=env)
    if res.exitcode == 0:
        print(res.stdout)
        fail(f'Command should fail but succeded with exit code {res.exitcode}: {cmd}')
    if ecode is not None:
        if res.exitcode != ecode:
            print(res.stdout)
            fail(f'Command should fail with exit code {ecode} but failed with {res.exitcode}: {cmd}')
        if res.exitcode == 1:
            # make sure there is no exception
            res2 = runCmd(cmd, onError='ignore', external=external, capture=True, dir=dir, env=env)
            if 'INTERNAL ERROR: checker raised an unexpected exception, this is a bug!' in res2.stdout:
                print(res2.stdout)
                fail(f'Command raised an exception')
    info('OK')
    return res

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
    pythonTestDirLocal = f'{praktomatTestsLocal}/python-prog1'
    python2TestDir = f'{praktomatTests}/python-prog2/'
    python2TestDirLocal = f'{praktomatTestsLocal}/python-prog2'
    localTestDir = f'{thisDir}/python-wypp'

    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 1,4', dir=localTestDir)
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 2', 121, dir=localTestDir)
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 2', 121, dir=localTestDir)
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 1,2', 121, dir=localTestDir)
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 3', 1, dir=localTestDir)
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {localTestDir} python --wypp {wyppDir} --sheet 01 --assignment 1,2,3', 1, dir=localTestDir)

    pythonTests = [('solution-good', 0), ('solution-wrapped', 0), ('solution-partial', 121), ('solution-partial-missing', 121),
                ('solution-fail', 121), ('solution-error', 1), ('solution-with-own-test-errors', 0),
                ('solution-timeout', 1)]

    for d, ecode in pythonTests:
        sheetDirLocal = f'{praktomatCheckersLocal}/multi-checker/tests/python-wypp/03'
        submissionDir = f'{localTestDir}/03/{d}/'
        cmd = f'python3 {checkScript} {checkScriptArgs} --submission-dir {submissionDir} python --wypp {wyppDir} --sheet 03'
        env = {'PRAKTOMAT_CHECKER_TEST_TIMEOUT': '2'}
        if ecode == 0:
            res = expectOk(cmd, external=sheetDirLocal, dir=submissionDir, env=env)
        else:
            res = expectFail(cmd, ecode, external=sheetDirLocal, dir=submissionDir, env=env)
        if d == 'solution-timeout':
            if 'timeout' not in res.stdout.lower():
                fail(f'expected timeout in output\n\n---\n{res.stdout}\n---')

    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pythonTestDir}/09/solution/ python --wypp {wyppDir} --sheet 09', external=f'{pythonTestDirLocal}/09', dir=f'{pythonTestDir}/09/solution/')

    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pythonTestDir}/labortest_2/solution/ python --wypp {wyppDir} --sheet labortest_2', external=f'{pythonTestDirLocal}/labortest_2', dir=f'{pythonTestDir}/labortest_2/solution/')
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pythonTestDir}/labortest_2/solution-partial/ python --wypp {wyppDir} --sheet labortest_2', 121, external=f'{pythonTestDirLocal}/labortest_2', dir=f'{pythonTestDir}/labortest_2/solution-partial/')
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pythonTestDir}/labortest_2/solution-nofiles/ python --wypp {wyppDir} --sheet labortest_2', 1, external=f'{pythonTestDirLocal}/labortest_2', dir=f'{pythonTestDir}/labortest_2/solution-nofiles/')

    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pythonTestDir}abschlussprojekt/solution-fail python --wypp {wyppDir} --sheet abschlussprojekt', external=f'{pythonTestDirLocal}/abschlussprojekt', dir=f'{pythonTestDir}abschlussprojekt/solution-fail')
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pythonTestDir}abschlussprojekt/solution-simple python --wypp {wyppDir} --sheet abschlussprojekt', 121, external=f'{pythonTestDirLocal}/abschlussprojekt', dir=f'{pythonTestDir}abschlussprojekt/solution-simple')
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pythonTestDir}abschlussprojekt/solution python --wypp {wyppDir} --sheet abschlussprojekt', external=f'{pythonTestDirLocal}/abschlussprojekt', dir=f'{pythonTestDir}abschlussprojekt/solution')
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pythonTestDir}10-dicts-exceptions/solution python --wypp {wyppDir} --sheet 10-dicts-exceptions', external=f'{pythonTestDirLocal}/10-dicts-exceptions', dir=f'{pythonTestDir}10/solution')
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pythonTestDir}10-dicts-exceptions/solution/subdir python --wypp {wyppDir} --sheet 10-dicts-exceptions', external=f'{pythonTestDirLocal}/10-dicts-exceptions', dir=f'{python2TestDir}P04-Listen/solution')

    prog2Sheets = ['P01-intro', 'P02-higher-order-funs', 'P03-OO', 'P04-Listen', 'P05-Sorting',
                   'P06-Sorting2', 'P07-Design-Patterns', 'P08-Trees', 'P09-Functional-Iterator',
                   'P11-Threads', 'P12-Hashing']
    prog2SheetsIncomplete = ['P01-intro', 'P06-Sorting2']
    for s in prog2Sheets:
        cmd = f'python3 {checkScript} {checkScriptArgs} --submission-dir {python2TestDir}{s}/solution python --wypp {wyppDir} --sheet {s}'
        external=f'{python2TestDirLocal}/{s}'
        dir=f'{python2TestDir}{s}/solution'
        if s in prog2SheetsIncomplete:
            expectFail(cmd, external=external, dir=dir, ecode=121)
        else:
            expectOk(cmd, external=external, dir=dir)

if runHaskellTests:
    printHeader('Running Haskell Tests')

    haskellTestDir = f'{praktomatTests}/haskell-advanced-prog'
    haskellTestDirLocal = f'{praktomatTestsLocal}/haskell-advanced-prog'
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/02 haskell --sheet 02', external=f'{haskellTestDirLocal}/02', dir=f'{haskellTestDir}/solutions/02')
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {thisDir}/haskell/02-no-file haskell --sheet 02', 1, external=f'{haskellTestDirLocal}/02', dir=f'{thisDir}/haskell/02-no-file')

    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {thisDir}/haskell/05-divide-by-zero/ haskell --sheet 05', 121, external=f'{haskellTestDirLocal}/05', dir=f'{thisDir}/haskell/05-divide-by-zero/')
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/01 haskell --sheet 01', 121, external=f'{haskellTestDirLocal}/01', dir=f'{haskellTestDir}/01/solution/')
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/03 haskell --sheet 03', external=f'{haskellTestDirLocal}/03', dir=f'{haskellTestDir}/03/solution/')
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/04 haskell --sheet 04', external=f'{haskellTestDirLocal}/04', dir=f'{haskellTestDir}/04/solution/')
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/05 haskell --sheet 05', external=f'{haskellTestDirLocal}/05', dir=f'{haskellTestDir}/05/solution/')
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/06 haskell --sheet 06', external=f'{haskellTestDirLocal}/06', dir=f'{haskellTestDir}/06/solution/')

    # Sheet 06 again, but with a nested solution directory
    with tempDir(dir=haskellTestDirLocal) as d:
        cp(f'{haskellTestDirLocal}/solutions/06', pjoin(d, 'solution'))
        expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pjoin(haskellTestDir, basename(d))} haskell --sheet 06', external=f'{haskellTestDirLocal}/06', dir=pjoin(haskellTestDir, basename(d)))

if runJavaTests:
    printHeader('Running Java Tests')

    javaTestDir = f'{praktomatTests}/java-aud'
    javaTestDirLocal = f'{praktomatTestsLocal}/java-aud'
    checkstyle = '/opt/praktomat-addons/checkstyle.jar' if useDocker else './checkstyle-10.3.4-all.jar'
    localTestDir = f'{thisDir}/java-aud'

    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {javaTestDir}/01-intro/solution java --checkstyle {checkstyle} --sheet 01-intro', external=f'{javaTestDirLocal}/01-intro', dir=f'{javaTestDir}/01-intro/solution')

    # Solution wrapped in another directory with failing tests
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {localTestDir}/passed-with-warnings/wrapper/ java --checkstyle {checkstyle} --sheet 01-intro', 121, external=f'{javaTestDirLocal}/01-intro', dir=f'{localTestDir}/passed-with-warnings/wrapper/')

    # Submission with BOM and iso encoding and with failing tests
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {localTestDir}/passed-with-warnings/AuD_Assignment_01/ java --checkstyle {checkstyle} --sheet 01-intro', 121, external=f'{javaTestDirLocal}/01-intro', dir=f'{localTestDir}/passed-with-warnings/AuD_Assignment_01/')

    # Submission with checkstyle errors
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {localTestDir}/fail/AuD_Assignment_01/ java --checkstyle {checkstyle} --sheet 01-intro', external=f'{javaTestDirLocal}/01-intro', dir=f'{localTestDir}/fail/AuD_Assignment_01/')

print()
info(f'{testCount} tests were run successfully!')
