from dataclasses import dataclass
from typing import Optional
from shell import *
import sys
import os
from utils import *
from common import *
from exercise import *
from testContext import *
from typing import *

def configError(s):
    abort('Config error: ' + s)

@dataclass
class PythonOptions(Options):
    sheet: str
    assignment: Optional[str]
    wypp: str

def prepareEnv(testEnv: Optional[dict], pyPath: Optional[str]):
    if testEnv is None:
        testEnv = {}
    else:
        testEnv = testEnv.copy()
    if pyPath:
        key = 'PYTHONPATH'
        oldPyPath = os.getenv(key)
        if oldPyPath:
            pyPath = pyPath + ':' + oldPyPath
        testEnv[key] = pyPath
    return testEnv

def runWypp(studentFile: str, wyppPath: str, onlyRunnable: bool, testFile: Optional[str]=None, testEnv: dict=None):
    thisDir = abspath('.')
    pyPath = wyppPath + '/python/site-lib:' + thisDir
    testEnv = prepareEnv(testEnv, pyPath)
    args = ['python3', wyppPath + '/python/src/runYourProgram.py']
    if testFile:
        args = args + ['--test-file', testFile]
    args = args + ['--check-runnable' if onlyRunnable else '--check', studentFile]
    debug(f'Command: {" ".join(args)}')
    res = run(args, onError='ignore', env=testEnv, stderrToStdout=True, captureStdout=True)
    return res

def runUnittest(testFile: str, searchDirs: list[Optional[str]], testEnv: dict=None):
    if not isFile(testFile):
        abort(f'Test file {testFile} does not exist')
    # important: testDir must come first so that the test module is taken from the testDir
    pyPath = dirname(testFile)
    for d in searchDirs:
        if d:
            pyPath = pyPath + ':' + d
    testEnv = prepareEnv(testEnv, pyPath)
    testMod = removeExt(basename(testFile))
    args = ['python3', '-m', 'unittest', testMod]
    debug(f'Command: {" ".join(args)}')
    res = run(args, onError='ignore', env=testEnv, stderrToStdout=True, captureStdout=True)
    return res

LoadStudentCodeStatus = Literal['ok', 'fail', 'not_found']

@dataclass
class LoadStudentCodeResult:
    status: LoadStudentCodeStatus
    output: str
    srcDir: Optional[str]

def loadStudentCode(opts: Options, p: str, checkLoad: bool) -> LoadStudentCodeResult:
    """
    Checks that the student file loads ok and that the student are successful.
    Executed from within source dir.
    """
    _out = ''
    def printOut(s='', emptyNewline=True):
        nonlocal _out
        if s or emptyNewline:
            _out = _out + s + '\n'
    _srcDir = None
    def mkResult(status: LoadStudentCodeStatus) -> LoadStudentCodeResult:
        return LoadStudentCodeResult(status, _out, _srcDir)
    studentFile = findFile(p, '.')
    if not studentFile:
        pyFilesList = run(f'find . -name "*.py"', captureStdout=splitLines, onError='ignore').stdout
        pyFiles = '\n'.join(pyFilesList)
        printOut(f'''ERROR: File {p} not part of the submission. I found the following files:

{pyFiles}''')
        return mkResult('not_found')
    _srcDir = dirname(studentFile)
    fixEncoding(studentFile)
    if not checkLoad:
        printOut(f'Only checking that file {studentFile} exists, not loading.')
        return mkResult('ok')
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
    res = loadStudentCode(opts, p, True)
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
        # FAILED (failures=1, errors=1, skipped=1)
        # OK
        # OK (skipped=5)
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
            if l.startswith('OK'):
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

def checkTutorTests(opts: Options, testCtx: TestContext, a: Assignment, srcDir: Optional[str]):
    """
    Checks the tutor tests. Executed from within the source dir.
    """
    for t in a.tests:
        testEnv = {'CHECK_ASSIGNMENT': a.id, 'CHECK_TEST': t}
        testPath = pjoin(sheetDir(opts), t)
        if a.pythonConfig.wypp:
            src = a.src
            if srcDir:
                src = pjoin(srcDir, a.src)
            testOut = runWypp(src, opts.wypp, onlyRunnable=False, testFile=testPath, testEnv=testEnv)
        else:
            testOut = runUnittest(testPath, [opts.wypp + '/python/site-lib', srcDir], testEnv=testEnv)
        testRes = getTestResult(t, testOut)
        testCtx.results.append(testRes)
        abortIfTestOkRequired(a, testRes)
    pass

def checkAssignments(opts: Options, ex: Exercise, allAss: list[Assignment]):
    """
    Checks the given assignments by checking if the code loads successfully and
    if it passes the tutor tests.
    Executed from within the source dir.

    This function is called if an exercise.yaml file exists.
    """
    allFiles = []
    for a in allAss:
        if a.src is not None and a.src not in [x[0] for x in allFiles]:
            allFiles.append((a.src, a.pythonConfig.wypp))
    ctx = CheckCtx.empty('Load and student tests')
    compileStatus = 'OK'
    missing = 0
    srcDirDict = {} # a.src -> directory where file is found
    for p, checkLoad in allFiles:
        res = loadStudentCode(opts, p, checkLoad)
        if res.srcDir:
            srcDirDict[p] = res.srcDir
        ctx.appendCompileOutput(res.output)
        match res.status:
            case 'fail':
                compileStatus = 'FAIL'
            case 'ok':
                pass
            case 'not_found':
                missing = missing + 1
                print(f'File {p} missing')
    if compileStatus == 'OK' and missing > 0:
        if missing == len(allFiles):
            compileStatus = 'FAIL'
            print('All files missing')
        else:
            compileStatus = 'OK_BUT_SOME_MISSING'
    ctx.compileStatus = compileStatus
    for a in allAss:
        testCtx = TestContext(assignment=a, sheet=ex.sheet, results=[])
        ctx.tests.append(testCtx)
        checkTutorTests(opts, testCtx, a, srcDirDict.get(a.src))
        checkScript(a, testCtx, sheetDir(opts))
    outputResultsAndExit(ctx)

def sheetDir(opts: Options):
    return getSheetDir(opts.testDir, opts.sheet)

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
