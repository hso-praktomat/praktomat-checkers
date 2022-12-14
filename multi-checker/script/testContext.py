from __future__ import annotations
from common import *
from utils import *
from shell import *
import re
from exercise import *

CompileStatus = Literal['OK', 'FAIL', 'OK_BUT_SOME_MISSING']
@dataclass
class CheckCtx:
    compileTitle: str
    compileStatus: CompileStatus
    compileOutput: Optional[str]
    tests: list[TestContext]
    @staticmethod
    def empty(t: str) -> CheckCtx:
        return CheckCtx(t, False, None, [])
    def appendCompileOutput(self, s: str):
        if self.compileOutput:
            self.compileOutput = self.compileOutput + '\n' + s
        else:
            self.compileOutput = s

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
    error: bool          # Running the test failed with an error
    totalTests: int = 0
    testErrors: int = 0
    testFailures: int = 0
    @property
    def isSuccess(self):
        return not self.error and self.testErrors == 0 and self.testFailures == 0

def outputResultsAndExit(ctx):
    # FIXME: no compile abstract!
    print(ctx.compileTitle + ' status: ' + ctx.compileStatus)
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
    printWithTitle(ctx.compileTitle + ' output', ctx.compileOutput)
    for testCtx in ctx.tests:
        for testRes in testCtx.results:
            title = f'Output for test of assignment {testCtx.assignment.id} ({testRes.testFile})'
            printWithTitle(title, testRes.testOutput)
            debug(testRes)
    match ctx.compileStatus:
        case 'FAIL':
            sys.exit(1)
        case 'OK_BUT_SOME_MISSING':
            sys.exit(OK_WITH_WARNINGS_EXIT_CODE)
        case 'OK':
            if notOkTotal > 0 or hasErrors:
                sys.exit(OK_WITH_WARNINGS_EXIT_CODE)
            else:
                sys.exit(0)

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
