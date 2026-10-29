from __future__ import annotations
from shell import *
from common import *
from utils import *
import re
from exercise import *
from i18n import tr

CompileStatus = Literal['OK', 'FAIL', 'OK_BUT_SOME_MISSING']

def compileStatusText(s: CompileStatus) -> str:
    match s:
        case 'OK':
            return 'OK'
        case 'FAIL':
            return tr('FAIL')
        case 'OK_BUT_SOME_MISSING':
            return tr('OK_BUT_SOME_MISSING')

@dataclass
class CheckCtx:
    compileTitle: str
    compileStatus: CompileStatus
    compileOutput: Optional[str]
    tests: list[TestContext]
    styleResult: Optional[StyleResult]=None
    outFile: Optional[str] = None
    @staticmethod
    def empty(t: str, outFile: Optional[str]) -> CheckCtx:
        return CheckCtx(t, 'FAIL', None, [], outFile=outFile)
    def appendCompileOutput(self, s: str) -> None:
        if self.compileOutput:
            self.compileOutput = self.compileOutput + '\n' + s
        else:
            self.compileOutput = s
    def asDict(self) -> dict[str, Any]:
        testList: list[dict[str, Any]] = []
        d = {'compileStatus': self.compileStatus, 'tests': testList}
        for t in self.tests:
            testList.append(t.asDict())
        return d
    def serialize(self, path: str) -> None:
        import pickle
        d = self.asDict()
        with open(path, 'wb') as f:
            pickle.dump(d, f)
        print(tr('Dumped test results to {file}', file=abspath(path)))

@dataclass
class TestContext:
    sheet: Optional[str]
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
    def asDict(self) -> dict[str, Any]:
        error = False
        totalTests = 0
        testErrors = 0
        testFailures = 0
        for r in self.results:
            if r.error:
                error = True
            totalTests += r.totalTests
            testErrors += r.testErrors
            testFailures += r.testFailures
        return {'sheet': self.sheet, 'assignment': self.assignment.id,
                'error': error, 'totalTests': totalTests, 'testErrors': testErrors,
                'testFailures': testFailures}

@dataclass
class TestResult:
    testFile: str
    testOutput: str
    error: bool          # Running the test failed with an error
    totalTests: int = 0
    testErrors: int = 0
    testFailures: int = 0
    @property
    def isSuccess(self) -> bool:
        return not self.error and self.testErrors == 0 and self.testFailures == 0

@dataclass
class StyleResult:
    hasErrors: bool
    styleOutput: Optional[str]
    @property
    def status(self) -> str:
        return tr('ERROR') if self.hasErrors else 'OK'

def outputResultsAndExit(ctx: CheckCtx, ecode: Optional[int]=None) -> None:
    if ctx.outFile:
        ctx.serialize(ctx.outFile)
    print(tr('{title} status: {status}', title=tr(ctx.compileTitle), status=compileStatusText(ctx.compileStatus)))
    notOkTotal = 0
    hasErrors = False
    totalPoints = 0
    possibleTotalPoints = 0
    if not ctx.tests:
        print(tr('No tests found'))
    else:
        print(tr('Test results:'))
        maxAssignmentIdLen = max([len(testCtx.assignment.id) for testCtx in ctx.tests])
        maxPoints = max([testCtx.assignment.points for testCtx in ctx.tests])
        maxPointsLen = len(f'{maxPoints:.1f}')
        for testCtx in ctx.tests:
            res = testCtx.summarizeResults()
            assPoints = testCtx.assignment.points
            assPointsFmt = f'{assPoints:.1f}'
            space1 = (maxPointsLen - len(assPointsFmt)) * ' '
            possibleTotalPoints += assPoints
            if res.error:
                zero = f'0.0/{assPoints:.1f} ' + tr('points') + ','
                shortResStr = f'{zero:15} ' + tr('ERROR')
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
                        pointsFmt = f'{points:.1f}'
                        space = (maxPointsLen - len(pointsFmt)) * ' '
                        pointsStr = f'{space}{pointsFmt}/{assPointsFmt} {space1}' + tr('points') + ','
                    else:
                        space = (maxPointsLen - 1) * ' '
                        pointsStr = f'{space}?/{assPointsFmt} {space1}' + tr('points') + ','
                    percentageStr = f'{percentage}% OK,'
                    rest = tr('({total} tests, {errors} errors, {failures} failures)', total=res.totalTests,
                              errors=res.testErrors, failures=res.testFailures)
                    shortResStr = f'{pointsStr:15} {percentageStr:10} {rest}'
                else:
                    space = (maxPointsLen - 1) * ' '
                    q = f'{space}?/{assPointsFmt} {space1}' + tr('points') + ','
                    shortResStr = f'{q:15} ' + tr('no tests')
            id = testCtx.assignment.id
            space = (maxAssignmentIdLen - len(id)) * ' '
            print(tr('Assignment {id}:', id=id) + f'{space} {shortResStr}')
    if ctx.styleResult != None:
        print('\n' + tr('Coding style: {status}', status=ctx.styleResult.status))
    print('\n' + tr('Total points: {points}/{max} (preliminary, subject to change!)', points=f'{totalPoints:.1f}',
                     max=f'{possibleTotalPoints:.1f}'))
    def printWithTitle(title: str, msg: str) -> None:
        delim = 2 * '=============================================================================='
        print()
        print(delim)
        print(title)
        print(delim)
        print()
        print(msg)
    if ctx.compileOutput:
        printWithTitle(tr('{title} output', title=tr(ctx.compileTitle)), ctx.compileOutput)
    if ctx.styleResult != None and ctx.styleResult.styleOutput != None:
        printWithTitle(tr('Output of style check'), ctx.styleResult.styleOutput)
    for testCtx in ctx.tests:
        for testRes in testCtx.results:
            title = tr('Output for test of assignment {id} ({file})', id=testCtx.assignment.id, file=testRes.testFile)
            printWithTitle(title, testRes.testOutput)
            debug(testRes)
    if ecode is not None:
        sys.exit(ecode)
    if ctx.styleResult is not None and ctx.styleResult.hasErrors:
        sys.exit(1)
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

def abortIfTestOkRequired(assignment: Assignment, result: TestResult, ctx: CheckCtx) -> None:
    if assignment.testOkRequired and not result.isSuccess:
        print(tr('Test for assignment {id} is required to succeed but failed!', id=assignment.id))
        print()
        print(result.testOutput)
        print()
        print(tr('Aborting'))
        outputResultsAndExit(ctx, ecode=1)

def checkScript(assignment: Assignment, ctx: TestContext, sheetDir: str, checkCtx: CheckCtx) -> None:
    script = assignment.testScript
    if not script:
        return
    scriptPath = pjoin(sheetDir, script)
    if not isFile(scriptPath):
        abort(tr('Script {file} does not exist', file=scriptPath))
    debug(f'Running {scriptPath}')
    scriptResult = run(scriptPath, onError='ignore', stderrToStdout=True, captureStdout=True)
    numErrors = 0 if (scriptResult.exitcode == 0) else 1
    testResult = TestResult(script, scriptResult.stdout, False, totalTests=1, testFailures=numErrors)
    ctx.results.append(testResult)
    abortIfTestOkRequired(assignment, testResult, checkCtx)
