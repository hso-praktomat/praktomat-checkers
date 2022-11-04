from __future__ import annotations
from common import *
from utils import *
from shell import *
import yaml
import re

@dataclass
class HaskellOptions(Options):
    sheet: str

@dataclass
class Assignment:
    sheet: str
    id: str
    points: int
    src: str         # the name of the source .hs file
    tests: list[str] # test files, can be empty
    testOkRequired: bool
    testScript: Optional[str]
    def parse(sheet: str, v: dict, id: int, defSrc: str):
        if v:
            src = v.get('src', defSrc)
            tests = asList(v.get('test', [])) + asList(v.get('tests', []))
            points = v.get('points', -1)
            try:
                points = int(points)
            except ValueError:
                bug('error parsing exercise.yaml: points must be a number')
            testOkRequired = v.get('test-ok-required', False)
            testScript = v.get('test-script')
        else:
            src = defSrc
            tests = []
            points = 0
            testOkRequired = False
            testScript = None
        return Assignment(sheet, id, points, src, tests, testOkRequired, testScript)

assignmentIdRe = re.compile(r'\d+[a-z]?')

@dataclass
class Exercise:
    sheet: str
    assignments: list[Assignment]
    def parse(sheet: str, ymlDict: dict) -> Exercise:
        defSrc = ymlDict.get('src')
        assignments = []
        for k, v in ymlDict.items():
            if type(k) == int:
                k = str(k)
            if type(k) != str or not assignmentIdRe.match(k):
                continue # not an assignment
            a = Assignment.parse(sheet, v, k, defSrc)
            assignments.append(a)
        return Exercise(sheet, assignments)

@dataclass
class CheckCtx:
    compileStatus: bool
    compileOutput: Optional[str]
    tests: list[TestContext]

@dataclass
class TestContext:
    sheet: str
    assignment: Assignment
    results: list[TestResult]
    def summarizeResults(self) -> TestResult:
        r = TestResult("?", "", False)
        for x in self.results:
            if x.error:
                r.error = True
            else:
                r.totalTests += x.totalTests
                r.testErrors += x.testErrors
                r.testFailures += x.testFailures
        return r

@dataclass
class TestResult:
    testFile: str
    testOutput: str
    error: bool
    totalTests: int = 0
    testErrors: int = 0
    testFailures: int = 0
    @property
    def isSuccess(self):
        return not self.error and self.testErrors == 0 and self.testFailures == 0

def parseExercise(sheet, yamlPath):
    s = readFile(yamlPath)
    ymlDict = yaml.load(s, Loader=yaml.FullLoader)
    return Exercise.parse(sheet, ymlDict)

def checkCompile(ctx: CheckCtx):
    cmd = 'stack test --only-locals'
    debug(f'Running "{cmd}"')
    result = run(cmd, onError='ignore', stderrToStdout=True, captureStdout=True)
    out = result.stdout
    if result.exitcode == 0:
        ctx.compileOutput = out
        ctx.compileStatus = True
    else:
        print(f'"{cmd}" failed\n\n{out}')
        findOut = run("find . -type f | xargs ls -l", onError='ignore', stderrToStdout=True, captureStdout=True).stdout
        debug(f"Directory listing:\n{findOut}")
        abort("Aborting")

haskellTestRe = re.compile(r'^Cases:\s*(\d+)\s*Tried:\s*(\d+)\s*Errors:\s*(\d+)\s*Failures:\s*(\d+)')
magicLine = "__START_TEST__"

def getTestResult(testFile, out):
    after = False
    lastTestLine = None
    out = out.replace('\r', '\n')
    for line in out.split('\n'):
        line = line.rstrip()
        if line == magicLine:
            after = True
        if after:
            m = haskellTestRe.match(line)
            if m:
                lastTestLine = line
    if lastTestLine:
        m = haskellTestRe.match(lastTestLine)
        # cases = int(m.group(1))
        tried = int(m.group(2))
        errors = int(m.group(3))
        failures = int(m.group(4))
        return TestResult(testFile, out, False, tried, errors, failures)
    else:
        return TestResult(testFile, out, True)

def abortIfTestOkRequired(assignment: Assignment, result: TestResult):
    if assignment.testOkRequired and not result.isSuccess:
        print(f'Test for assignment {assignment.id} is required to succeed but failed!')
        print()
        print(result.testOutput)
        print()
        abort(f'Aborting')

def checkScript(assignment: Assignment, ctx: TestContext, sheetDir: str):
    script = assignment.testScript
    if not script:
        return
    scriptPath = pjoin(sheetDir, script)
    if not isFile(scriptPath):
        abort(f'Script {scriptPath} does not exist')
    debug(f'Running {scriptPath}')
    scriptResult = run(scriptPath, onError='ignore', stderrToStdout=True, captureStdout=True)
    numErrors = 0 if (scriptResult.exitcode == 0) else 1
    testResult = TestResult(script, scriptResult.stdout, False, totalTests=1, testErrors=numErrors)
    ctx.results.append(testResult)
    abortIfTestOkRequired(assignment, testResult)

def checkTest(assignment: Assignment, ctx: TestContext, testFile: str, incDirs: list[str]):
    prjName = 'ap' + str(assignment.sheet)
    testModName = removeExt(basename(testFile))
    srcFile = assignment.src
    incOpts = []
    for d in incDirs:
        incOpts.append(f'--ghci-options -i{d}')
    cmd = f'''stack ghci "{srcFile}" "{testFile}" --flag {prjName}:test-mode
        {" ".join(incOpts)}
        --ghci-options -e --ghci-options {testModName}.tutorMain'''
    debug(f'Executing tests {testFile} for {srcFile} ...')
    debug(f'Command: {cmd}')
    result = run(cmd, onError='ignore', stderrToStdout=True, captureStdout=True)
    testResult = getTestResult(testFile, 'Command: ' + cmd + '\n\n' + result.stdout)
    ctx.results.append(testResult)
    abortIfTestOkRequired(assignment, testResult)

def outputResults(ctx):
    print('Compile status: ' + ('OK' if ctx.compileStatus else 'FAIL'))
    notOkTotal = 0
    hasErrors = False
    totalPoints = 0
    possibleTotalPoints = 0
    print('Test results:')
    for testCtx in ctx.tests:
        res = testCtx.summarizeResults()
        assPoints = testCtx.assignment.points
        possibleTotalPoints += assPoints
        if res.error:
            zero = f'0.0/{assPoints:.1f} points,'
            shortResStr = f'{zero:15} ERROR'
            hasErrors = True
        else:
            if res.totalTests > 0:
                notOk = res.testErrors + res.testFailures
                notOkTotal += notOk
                ok = res.totalTests - notOk
                ratio = ok / res.totalTests
                percentage = round(100 * ratio)
                if assPoints > 0:
                    points = round(ratio * assPoints, 1)
                    totalPoints = totalPoints + points
                    pointsStr = f'{points:.1f}/{assPoints:.1f} points,'
                else:
                    pointsStr = f'???/{assPoints} points,'
                percentageStr = f'{percentage}% OK,'
                rest = f'({res.totalTests} tests, {res.testErrors} errors, {res.testFailures} failures)'
                shortResStr = f'{pointsStr:15} {percentageStr:10} {rest}'
            else:
                q = f'???/{assPoints:.1f} points,'
                shortResStr = f'{q:15} no tests'
        print(f'Assignment {testCtx.assignment.id}: {shortResStr}')
    print(f'\nTotal points: {totalPoints:.1f}/{possibleTotalPoints:.1f} (preliminary, subject to change!)')
    def printWithTitle(title, msg):
        delim = 2 * '=============================================================================='
        print()
        print(delim)
        print(title)
        print(delim)
        print()
        print(msg)
    printWithTitle('Compile output', ctx.compileOutput)
    for testCtx in ctx.tests:
        for testRes in testCtx.results:
            title = f'Output for test of assignment {testCtx.assignment.id} ({testRes.testFile})'
            printWithTitle(title, testRes.testOutput)
            debug(testRes)
    if notOkTotal > 0 or hasErrors:
        sys.exit(OK_WITH_WARNINGS_EXIT_CODE)
    else:
        sys.exit(0)

def doCheck(srcDir, testDir, sheet):
    sheetDir = pjoin(testDir, 'sheet-' + sheet)
    cp(pjoin(sheetDir, 'package.yaml'), '.')
    cp(pjoin(testDir, 'stack.yaml'), '.')
    exFile = pjoin(sheetDir, 'exercise.yaml')
    ex = parseExercise(sheet, exFile)
    debug(f'Exercise (file: {exFile}): {ex}')
    hsFiles = run(f'find {srcDir} -name "*.hs"', captureStdout=splitLines).stdout
    for x in hsFiles:
        target = x.removeprefix(srcDir).lstrip('/')
        targetDir = dirname(target)
        if targetDir:
            mkdir(targetDir, createParents=True)
        cp(x, target)
    # do the checks
    for a in ex.assignments:
        if not isFile(a.src):
            print(f'ERROR: File {a.src} not included in submission')
            sys.exit(OK_WITH_WARNINGS_EXIT_CODE)
    ctx = CheckCtx(False, None, [])
    checkCompile(ctx)
    for a in ex.assignments:
        testCtx = TestContext(assignment=a, sheet=sheet, results=[])
        ctx.tests.append(testCtx)
        for t in a.tests:
            checkTest(a, testCtx, pjoin(sheetDir, t), [pjoin(testDir, 'lib'), sheetDir])
        checkScript(a, testCtx, sheetDir)
    outputResults(ctx)

def check(opts: Options):
    srcDir = abspath(opts.sourceDir)
    testDir = abspath(opts.testDir)
    with tempDir(dir='.') as d:
        with workingDir(d):
            debug(f"Running Haskell checks from directory {d}")
            doCheck(srcDir, testDir, opts.sheet)
