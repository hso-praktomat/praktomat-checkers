from dataclasses import dataclass
from typing import Optional
from shell import *
import sys
import os
from utils import *
from common import *
from exercise import *
from testContext import *

def configError(s):
    abort('Config error: ' + s)

@dataclass
class PythonOptions(Options):
    sheet: str
    assignment: Optional[str]
    wypp: str

def runWypp(studentFile: str, wyppPath: str, onlyRunnable: bool, testFile: Optional[str]=None,
            capture: bool=False):
    thisDir = abspath('.')
    env = {'PYTHONPATH': wyppPath + '/python/src:' + wyppPath + '/python/site-lib:' + thisDir}
    print()
    args = ['python3', wyppPath + '/python/src/runYourProgram.py']
    if testFile:
        args = args + ['--test-file', testFile]
    args = args + ['--check-runnable' if onlyRunnable else '--check', studentFile]
    if capture:
        res = run(args, onError='ignore', env=env, stderrToStdout=True, captureStdout=True)
    else:
        res = run(args, onError='ignore', env=env)
    print()
    return res

def checkFileLoadsOk(opts: Options, p: str):
    """
    Checks that the student file loads ok and that the student are successful.
    Executed from within sourcde dir.
    """
    studentFile = findFile(p, '.')
    if not studentFile:
        pyFilesList = run(f'find . -name "*.py"', captureStdout=splitLines, onError='ignore').stdout
        pyFiles = '\n'.join(pyFilesList)
        print(f'''FEHLER: Datei {p} nicht in Abgabe enthalten.

Folgende Dateien mit der Endung .py wurden gefunden:

{pyFiles}''')
        sys.exit(OK_WITH_WARNINGS_EXIT_CODE)
    fixEncoding(studentFile)
    print()
    print(f'## Überprüfe dass {p} beim Laden keinen Fehler verursacht ...')
    runRes = runWypp(studentFile, opts.wypp, onlyRunnable=True)
    if runRes.exitcode == 0:
        print(f'## OK: {p} erfolgreich geladen')
    else:
        abort(f'''Datei {p} konnte nicht geladen werden.
Weiter oben finden Sie die Fehlermeldungen.''')
    print()
    print(f'## Führe Tests in {p} aus ...')
    testRes = runWypp(studentFile, opts.wypp, onlyRunnable=False)
    if testRes.exitcode == 0:
        print(f'## OK: keine Testfehler in {p}')
    else:
        abort(f'''Datei {p} enthält fehlerhafte Tests
Falls Sie einen Test nicht zum Laufen bringen, müssen
Sie diesen Test auskommentieren.''')

class PythonTestResult:
    @staticmethod
    def parseWyppResult(testFile: str, s: str):
        r1 = re.compile(r'^Tutor:\s*(\d+) Tests, (\d+) Fehler')
        r2 = re.compile(r'^Tutor:\s*(\d+) Tests, alle erfolgreich')
        for l in s.split('\n'):
            m1 = r1.match(l)
            m2 = r2.match(l)
            if m1 or m2:
                if m1:
                    total = int(m1.group(1))
                    fail = int(m1.group(2))
                else:
                    total = int(m2.group(1))
                    fail = 0
                return TestResult(testFile=testFile, testOutput=s, error=False, totalTests=total,
                        testFailures=fail, testErrors=0)
    @staticmethod
    def parseUnitResult(testFile: str, s: str):
        # Ran 3 tests in 0.000s
        # FAILED (errors=1)
        # FAILED (failures=1, errors=1)
        # OK
        total = -1
        errors = 0
        failures = 0
        skipped = 0
        r = re.compile('^Ran (\\d+) test')
        def getKv(l, k):
            r = re.compile(f'{k}=(\\d+)')
            m = r.search(l)
            if m:
                return int(m.group(1))
            else:
                return 0
        for l in s.split('\n'):
            l = l.strip()
            m = r.match(l)
            if m:
                total = int(m.group(1))
            if l.startswith('FAILED'):
                errors = getKv(l, 'errors')
                failures = getKv(l, 'failures')
                skipped = getKv(l, 'skipped')
        if total > 0:
            return TestResult(testFile=testFile, testOutput=s, error=False,
                    totalTests=(total - skipped), testFailures=failures, testErrors=errors)

def getTestResult(testFile, runRes: RunResult):
    r = PythonTestResult.parseWyppResult(testFile, runRes.stdout)
    if r:
        return r
    r = PythonTestResult.parseUnitResult(testFile, runRes.stdout)
    if r:
        return r
    return TestResult(testFile=testFile, testOutput=runRes.stdout, error=(runRes.exitcode != 0),
            totalTests=0, testFailures=0, testErrors=0)

def checkTutorTests(opts: Options, testCtx: TestContext, a: Assignment):
    """
    Checks the tutor tests. Executed from within the source dir.
    """
    for t in a.tests:
        testPath = pjoin(sheetDir(opts), t)
        testOut = runWypp(a.src, opts.wypp, onlyRunnable=False, testFile=testPath, capture=True)
        testRes = getTestResult(t, testOut)
        testCtx.results.append(testRes)
        abortIfTestOkRequired(a, testRes)
    pass

def checkAssignments(opts: Options, ex: Exercise, allAss: list[Assignment]):
    allFiles = []
    for a in allAss:
        if a.src not in allFiles:
            allFiles.append(a.src)
    for p in allFiles:
        checkFileLoadsOk(opts, p)
    ctx = CheckCtx.empty(False)
    for a in allAss:
        testCtx = TestContext(assignment=a, sheet=ex.sheet, results=[])
        ctx.tests.append(testCtx)
        checkTutorTests(opts, testCtx, a)
        checkScript(a, testCtx, sheetDir(opts))
    outputResults(ctx)

def sheetDir(opts: Options):
    return pjoin(opts.testDir, 'sheet-' + opts.sheet)

def getExercise(opts: Options) -> Optional[Exercise]:
    sheet = opts.sheet
    exFile = pjoin(sheetDir(opts), 'exercise.yaml')
    if isFile(exFile):
        return parseExercise(sheet, exFile)
    else:
        return None

def check(opts: Options):
    ex = getExercise(opts)
    ass = opts.assignment
    with workingDir(opts.sourceDir):
        if ex is None:
            if ass is None:
                configError(f'Option --assignment not found, no exercise file found')
            p = f'aufgabe_{opts.assignment.zfill(2)}.py'
            checkFileLoadsOk(opts, p)
        else:
            if ass is None:
                allAss = ex.assignments
            else:
                allAss = [a for a in ex.assignments if a.id == ass]
            checkAssignments(opts, ex, allAss)
