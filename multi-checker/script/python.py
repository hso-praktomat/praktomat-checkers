from dataclasses import dataclass
from typing import Optional
from shell import *
import sys
import os
from utils import *
from common import *
from exercise import *
from testContext import *
from pythonStyle import checkStyle
from i18n import tr, trKey, getLang
from typing import *

def configError(s: str) -> NoReturn:
    abort(tr('Config error: {msg}', msg=s))

@dataclass
class PythonOptions(Options):
    sheet: Optional[str]
    assignments: Optional[str | list[str]]
    wypp: str
    styleCheck: bool

def prepareEnv(testEnv: Optional[dict[str, str]], searchDirs: list[str]) -> dict[str, str]:
    if testEnv is None:
        testEnv = {}
    else:
        testEnv = testEnv.copy()
    if searchDirs:
        l: list[str] = []
        for x in searchDirs:
            x = x.strip()
            if not x:
                x = '.'
            x = os.path.normpath(x)
            if x not in l:
                l.append(x)
        searchDirs = l
        key = 'PYTHONPATH'
        pyPath = ':'.join(searchDirs)
        oldPyPath = os.getenv(key)
        if oldPyPath:
            pyPath = pyPath + ':' + oldPyPath
        testEnv[key] = pyPath
    return testEnv

def stripBlankLines(s: str) -> str:
    """
    Removes blank lines at the start and the end of s.
    """
    lines = s.split('\n')
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return '\n'.join(lines)

# Exit code of WYPP (>= 2.5.2) with --check if the file loaded but some checks failed. If loading the
# file or the test file crashed, the exit code is 1.
WYPP_CHECKS_FAILED_EXIT_CODE = 3

def runWypp(studentFile: str, wyppPath: str, typecheck: bool, testFile: Optional[str]=None,
            testEnv: Optional[dict[str, str]]=None, timeout: Optional[int]=None) -> RunResult:
    thisDir = abspath('.')
    # print('pyPath='+pyPath)
    testEnv = prepareEnv(testEnv, [wyppPath + '/python/code:', thisDir])
    args = ['python3', wyppPath + '/python/code/wypp/runYourProgram.py', '--lang', getLang()]
    if testFile:
        args = args + ['--test-file', testFile]
    args = args + ['--check']
    if not typecheck:
        args = args + ['--no-typechecking']
    args = args + [studentFile]
    res = runWithTimeout(args, timeout, tr('running {file} via WYPP, testFile={testFile}', file=studentFile,
                                            testFile=testFile),
                         env=testEnv)
    # WYPP prints 10 empty lines before its banner
    return RunResult(stripBlankLines(res.stdout), res.stderr, res.exitcode)

def runUnittest(testFile: str, searchDirs: list[str], testEnv: Optional[dict[str, str]]=None,
                timeout: Optional[int]=None) -> RunResult:
    if not isFile(testFile):
        abort(tr('Test file {file} does not exist', file=testFile))
    testEnv = prepareEnv(testEnv, ['.'] + searchDirs)
    args = ['python3', testFile]
    res = runWithTimeout(args, timeout, tr('running unittests in {file}', file=testFile), env=testEnv)
    return res

LoadStudentCodeStatus = Literal['ok', 'fail', 'not_found']

@dataclass
class LoadStudentCodeResult:
    status: LoadStudentCodeStatus
    output: str
    srcDir: Optional[str]
    studentFile: Optional[str]

LoadCheck = Literal['dont-load', 'load-no-typecheck', 'load-typecheck']

def loadStudentCode(opts: PythonOptions, p: str, checkLoad: LoadCheck, styleCheck: bool) -> LoadStudentCodeResult:
    """
    Checks that the student file loads ok and that the student tests are successful. Then, if
    styleCheck is set and the file loaded ok, checks its coding conventions; a violation makes
    the file fail. Executed from within source dir.
    """
    if checkLoad not in ['dont-load', 'load-no-typecheck', 'load-typecheck']:
        raise ValueError('Invalid value for checkLoad argument: ' + str(checkLoad))
    _out = ''
    def printOut(s: str='', emptyNewline: bool=True) -> None:
        nonlocal _out
        if s or emptyNewline:
            _out = _out + s + '\n'
    _srcDir = None
    _studentFile = None
    def mkResult(status: LoadStudentCodeStatus) -> LoadStudentCodeResult:
        return LoadStudentCodeResult(status, _out, _srcDir, _studentFile)
    def checkConventions(studentFile: str) -> LoadStudentCodeStatus:
        if not styleCheck:
            return 'ok'
        printOut()
        printOut(tr('## Checking coding conventions of {file} ...', file=p))
        res = checkStyle([studentFile])
        if res is None:
            printOut(tr('{file}: coding conventions not checked because of syntax errors', file=p))
            return 'ok'
        if res.hasErrors:
            printOut(res.styleOutput or '')
            printOut()
            printOut(tr('File {file} violates the coding conventions.', file=p))
            return 'fail'
        printOut(tr('## OK: {file} follows the coding conventions', file=p))
        return 'ok'
    studentFile = findFile(p, '.', ignoreCase=True)
    if not studentFile:
        pyFilesList = run(f'find . -name "*.py"', captureStdout=splitLines, onError='ignore').stdout
        pyFiles = '\n'.join(pyFilesList[:20])
        printOut(tr('ERROR: File {file} not part of the submission. I found the following files:\n\n{files}',
                    file=p, files=pyFiles))
        return mkResult('not_found')
    _srcDir = dirname(studentFile)
    _studentFile = studentFile
    fixEncoding(studentFile)
    if checkLoad == 'dont-load':
        printOut(tr('Only checking that file {file} exists, not loading.', file=studentFile))
        return mkResult(checkConventions(studentFile))
    printOut()
    printOut(tr('## Loading {file} and executing its tests ...', file=p))
    # A single run of WYPP: its exit code tells a crash while loading from failing checks
    runRes = runWypp(studentFile, opts.wypp, typecheck=checkLoad == 'load-typecheck',
                     timeout=testTimeoutSeconds())
    printOut(runRes.stdout, emptyNewline=False)
    if runRes.exitcode == 0:
        printOut(tr('## OK: {file} loads successfully and has no test failures', file=p))
    elif runRes.exitcode == WYPP_CHECKS_FAILED_EXIT_CODE:
        printOut(tr('## OK: {file} loads successfully', file=p))
        printOut(tr('File {file} contains test failures!\n'
                    'If you cannot make a test succeed, you have to comment it out.', file=p))
    elif runRes.exitcode == TIMEOUT_EXIT_CODE:
        printOut(tr('Timeout while running {file}. Probably there is an infinite loop!', file=p))
        return mkResult('fail')
    else:
        printOut(tr('File {file} could not be loaded.', file=p))
        return mkResult('fail')
    return mkResult(checkConventions(studentFile))

def checkFileLoadsOk(opts: PythonOptions, p: str) -> LoadStudentCodeResult:
    res = loadStudentCode(opts, p, 'load-typecheck', opts.styleCheck)
    print(res.output)
    return res

def checkAssignmentsLoadOk(opts: PythonOptions, ass: str | list[str] | None) -> None:
    if isinstance(ass, str):
        ass = [ass]
    elif ass is None:
        ass = []
    delim = '=============================================================================='
    stats: list[tuple[str, LoadStudentCodeStatus]] = []
    for x in ass:
        possible_filenames = [
            f'aufgabe_{x.zfill(2)}.py',
            f'aufgabe_{x}.py',
            f'aufgabe{x.zfill(2)}.py',
            f'aufgabe{x}.py',
            f'aufgabe-{x.zfill(2)}.py',
            f'aufgabe-{x}.py',
        ]
        # Use a default file name in case none is found.
        # The script will then fail at a later point.
        p = possible_filenames[0]
        for name in possible_filenames:
            if findFile(name, '.', ignoreCase=True) is not None:
                p = name
                break
        print(f'\n{delim}')
        print(tr('Checking assignment {id} (file: {file})', id=x, file=p))
        res = checkFileLoadsOk(opts, p)
        stats.append((p, res.status))
    print('\n')
    print(delim)
    print(tr('Summary'))
    print()
    warn = False
    err = False
    for (p, stat) in stats:
        match stat:
            case 'not_found':
                print(tr('{file}: not found', file=p))
                warn = True
            case 'fail':
                print(tr('{file}: failed', file=p))
                err = True
            case 'ok':
                pass
    print()
    if err:
        print(tr('Error: at least one assignment failed!'))
        sys.exit(1)
    if warn:
        print(tr('Warn: at least one assignment not found'))
        sys.exit(OK_WITH_WARNINGS_EXIT_CODE)

class PythonTestResult:
    @staticmethod
    def parseWyppResult(testFile: str, s: str) -> Optional[TestResult]:
        # Summary of WYPP in German or English, e.g. "Tutor:  6 Tests, 4 Fehler" or "Tutor:  6 tests, 4 errors"
        r1 = re.compile(r'^Tutor:\s*(\d+) [Tt]ests?, (\d+) (?:Fehler|errors?)')
        r2 = re.compile(r'^Tutor:\s*(\d+) [Tt]ests?, (?:alle erfolgreich|all successful)')
        for l in s.split('\n'):
            m1 = r1.match(l)
            m2 = r2.match(l)
            if m1 or m2:
                total = 0
                fail = 0
                if m1:
                    total = int(m1.group(1))
                    fail = int(m1.group(2))
                elif m2:
                    total = int(m2.group(1))
                    fail = 0
                return TestResult(testFile=testFile, testOutput=s, error=False, totalTests=total,
                        testFailures=fail, testErrors=0)
    @staticmethod
    def parseUnitResult(testFile: str, s: str) -> Optional[TestResult]:
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
        def getKv(l: str, k: str) -> int:
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

def getTestResult(testFile: str, runRes: RunResult) -> TestResult:
    r = PythonTestResult.parseWyppResult(testFile, runRes.stdout)
    if r:
        return r
    r = PythonTestResult.parseUnitResult(testFile, runRes.stdout)
    if r:
        return r
    return TestResult(testFile=testFile, testOutput=runRes.stdout, error=(runRes.exitcode != 0),
            totalTests=0, testFailures=0, testErrors=0)

def checkTutorTests(opts: PythonOptions,
                    testCtx: TestContext,
                    a: Assignment,
                    srcDir: Optional[str],
                    checkCtx: CheckCtx) -> None:
    """
    Checks the tutor tests. Executed from within the source dir.
    """
    for t in a.tests:
        testEnv = {'CHECK_ASSIGNMENT': a.id, 'CHECK_TEST': t}
        testPath = pjoin(sheetDir(opts), t)
        if a.pythonConfig.wypp:
            src = a.src
            if src is None:
                abort(tr('Configuration error: src option not set for assignment {id}', id=a.id))
                return
            if srcDir:
                src = pjoin(srcDir, src)
            testOut = runWypp(src, opts.wypp,
                              typecheck=a.pythonConfig.typecheck,
                              testFile=testPath, testEnv=testEnv, timeout=testTimeoutSeconds())
        else:
            searchDirs = [opts.wypp + '/python/code']
            if srcDir:
                searchDirs.append(srcDir)
            testOut = runUnittest(testPath, searchDirs,
                                  testEnv=testEnv, timeout=testTimeoutSeconds())
        testRes = getTestResult(t, testOut)
        testCtx.results.append(testRes)
        abortIfTestOkRequired(a, testRes, checkCtx)
    pass

def checkAssignments(opts: PythonOptions, ex: Exercise, allAss: list[Assignment]) -> None:
    """
    Checks the given assignments by checking if the code loads successfully and
    if it passes the tutor tests.
    Executed from within the source dir.

    This function is called if an exercise.yaml file exists.
    """
    allFiles: list[tuple[str, LoadCheck]] = []
    extras: set[str] = set()
    for a in allAss:
        if a.src is not None and a.src not in [x[0] for x in allFiles]:
            checkLoad: LoadCheck = 'dont-load'
            pc = a.pythonConfig
            if pc.typecheck:
                checkLoad = 'load-typecheck'
            elif pc.checkLoad:
                checkLoad = 'load-no-typecheck'
            allFiles.append((a.src, checkLoad))
            for e in a.extraFiles:
                extras.add(e)
    for e in extras:
        cp(pjoin(sheetDir(opts), e), '.')
    # Lenient: the coding conventions of a file are not checked if one of its assignments disables the check
    noStyleCheck = set([a.src for a in allAss if not a.pythonConfig.style])
    ctx = CheckCtx.empty(trKey('Load and student tests'), opts.resultFile)
    compileStatus = 'OK'
    missing = 0
    srcDirDict: dict[str, str] = {} # a.src -> directory where file is found
    for p, checkLoad in allFiles:
        res = loadStudentCode(opts, p, checkLoad, opts.styleCheck and p not in noStyleCheck)
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
                # print(f'File {p} missing')
    if compileStatus == 'OK' and missing > 0:
        if missing == len(allFiles):
            compileStatus = 'FAIL'
            print(tr('All files missing'))
        else:
            compileStatus = 'OK_BUT_SOME_MISSING'
    ctx.compileStatus = compileStatus
    for a in allAss:
        testCtx = TestContext(assignment=a, sheet=ex.sheet, results=[])
        ctx.tests.append(testCtx)
        checkTutorTests(opts, testCtx, a, srcDirDict.get(a.src) if a.src is not None else None, ctx)
        checkScript(a, testCtx, sheetDir(opts), ctx)
    outputResultsAndExit(ctx)

def sheetDir(opts: PythonOptions) -> str:
    return getSheetDir(opts.testDir, opts.sheet)

def check(opts: PythonOptions) -> None:
    sheet = opts.sheet
    exFile = pjoin(sheetDir(opts), 'exercise.yaml')
    if isFile(exFile):
        ex = parseExercise(sheet, exFile)
    else:
        ex = None
    debug(f'Exercise (file: {exFile}): {ex}')
    ass = opts.assignments
    nestedSourceDir = findSolutionDir(opts.sourceDir)
    with workingDir(nestedSourceDir):
        if ex is None:
            if ass is None:
                configError(tr('Option --assignment not given, exercise file {file} not found', file=exFile))
            checkAssignmentsLoadOk(opts, ass)
        else:
            if ass is None:
                allAss = ex.assignments
            else:
                l = asList(ass)
                ex.ensureAssignmentsDefined(l)
                allAss = [a for a in ex.assignments if a.id in l]
            checkAssignments(opts, ex, allAss)
