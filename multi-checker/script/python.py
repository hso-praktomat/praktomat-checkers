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

def runWypp(studentFile: str, wyppPath: str, onlyRunnable: bool, testFile: Optional[str]=None):
    thisDir = abspath('.')
    env = {'PYTHONPATH': wyppPath + '/python/src:' + wyppPath + '/python/site-lib:' + thisDir}
    args = ['python3', wyppPath + '/python/src/runYourProgram.py']
    if testFile:
        args = args + ['--test-file', testFile]
    args = args + ['--check-runnable' if onlyRunnable else '--check', studentFile]
    res = run(args, onError='ignore', env=env, stderrToStdout=True, captureStdout=True)
    return res

LoadStudentCodeStatus = Literal['ok', 'fail', 'not_found']

@dataclass
class LoadStudentCodeResult:
    status: LoadStudentCodeStatus
    output: str

def loadStudentCode(opts: Options, p: str) -> LoadStudentCodeResult:
    """
    Checks that the student file loads ok and that the student are successful.
    Executed from within source dir.
    """
    _out = ''
    def printOut(s='', emptyNewline=True):
        nonlocal _out
        if s or emptyNewline:
            _out = _out + s + '\n'
    def mkResult(status: LoadStudentCodeStatus) -> LoadStudentCodeResult:
        return LoadStudentCodeResult(status, _out)
    studentFile = findFile(p, '.')
    if not studentFile:
        pyFilesList = run(f'find . -name "*.py"', captureStdout=splitLines, onError='ignore').stdout
        pyFiles = '\n'.join(pyFilesList)
        printOut(f'''ERROR: File {p} not part of the submission. I found the following files:

{pyFiles}''')
        return mkResult('not_found')
    fixEncoding(studentFile)
    printOut()
    printOut(f'## Checking that {p} loads successfully ...')
    runRes = runWypp(studentFile, opts.wypp, onlyRunnable=True)
    printOut(runRes.stdout, emptyNewline=False)
    if runRes.exitcode == 0:
        printOut(f'## OK: {p} loads successfully')
    else:
        printOut(f'''File {p} could not be loaded.
You find more error messages above.''')
        return mkResult('fail')
    printOut()
    printOut(f'## Executing tests in {p} ...')
    testRes = runWypp(studentFile, opts.wypp, onlyRunnable=False)
    printOut(testRes.stdout, emptyNewline=False)
    if testRes.exitcode == 0:
        printOut(f'## OK: no test failures in {p}')
    else:
        printOut(f'''File {p} contains test failures!
If you cannot make a test succeed, you have to comment it out.''')
        return mkResult('fail')
    return mkResult('ok')

def checkFileLoadsOk(opts: Options, p: str):
    res = loadStudentCode(opts, p)
    print(res.output)
    match res.status:
        case 'not_found':
            sys.exit(OK_WITH_WARNINGS_EXIT_CODE)
        case 'fail':
            sys.exit(1)

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
        testOut = runWypp(a.src, opts.wypp, onlyRunnable=False, testFile=testPath)
        testRes = getTestResult(t, testOut)
        testCtx.results.append(testRes)
        abortIfTestOkRequired(a, testRes)
    pass

def checkAssignments(opts: Options, ex: Exercise, allAss: list[Assignment]):
    """
    Checks the given assignments by checking if the code loads successfully and
    if it passes the tutor tests.
    Executed from within the source dir.
    """
    allFiles = []
    for a in allAss:
        if a.src not in allFiles:
            allFiles.append(a.src)
    ctx = CheckCtx.empty('Load and student tests')
    for p in allFiles:
        res = loadStudentCode(opts, p)
        ctx.appendCompileOutput(res.output)
        match res.status:
            case 'fail':
                ctx.compileStatus = 'FAIL'
            case 'ok':
                ctx.compileStatus = 'OK'
            case 'not_found':
                ctx.compileStatus = 'OK_BUT_SOME_MISSING'
    for a in allAss:
        testCtx = TestContext(assignment=a, sheet=ex.sheet, results=[])
        ctx.tests.append(testCtx)
        checkTutorTests(opts, testCtx, a)
        checkScript(a, testCtx, sheetDir(opts))
    outputResultsAndExit(ctx)

def sheetDir(opts: Options):
    return pjoin(opts.testDir, 'sheet-' + opts.sheet)

def check(opts: Options):
    sheet = opts.sheet
    exFile = pjoin(sheetDir(opts), 'exercise.yaml')
    if isFile(exFile):
        ex = parseExercise(sheet, exFile)
    else:
        ex = None
    ass = opts.assignment
    with workingDir(opts.sourceDir):
        if ex is None:
            if ass is None:
                configError(f'Option --assignment not given, exercise file {exFile} not found')
            p = f'aufgabe_{opts.assignment.zfill(2)}.py'
            checkFileLoadsOk(opts, p)
        else:
            if ass is None:
                allAss = ex.assignments
            else:
                allAss = [a for a in ex.assignments if a.id == ass]
            checkAssignments(opts, ex, allAss)
