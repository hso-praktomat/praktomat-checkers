from __future__ import annotations
from common import *
from utils import *
from shell import *
import re
import os
import os.path
from exercise import *
from testContext import *
import xml.etree.ElementTree as ET

# Checking Java code using Gradle

@dataclass
class JavaOptions(Options):
    sheet: str
    checkstylePath: str

defaultBuildFile = pjoin(os.path.realpath(os.path.dirname(__file__)), 'build.gradle.kts')
checkstyleConfig = pjoin(os.path.realpath(os.path.dirname(__file__)), 'checkstyle.xml')

def execGradle(task: str, studentDir: str, testDir: str='test-src', testFilter: str='*'):
    buildFile = pjoin(studentDir, '..', 'build.gradle.kts')
    cmd = [
        'gradle',
        '-b',
        buildFile,
        '-PtestFilter=' + testFilter,
        '-PtestDir=' + testDir,
        '-PstudentDir=' + studentDir,
        task,
        '--rerun-tasks',
        '--no-parallel',
        '--max-workers=1',
        '--no-daemon',
        '--offline',
        '--warning-mode=none',
        '-Dorg.gradle.welcome=never'
    ]
    debug(f'Running "{cmd}"')
    return run(cmd, onError='ignore', stderrToStdout=True, captureStdout=True)

def checkCompile(ctx: CheckCtx, srcDir: str):
    result = execGradle('compileJava', studentDir=srcDir)
    out = result.stdout
    if result.exitcode == 0:
        ctx.compileOutput = out
        ctx.compileStatus = 'OK'
    else:
        print(f'Compiling failed\n\n{out}')
        findOut = run('find . -type f | xargs ls -l', onError='ignore', stderrToStdout=True, captureStdout=True).stdout
        debug(f'Directory listing:\n{findOut}')
        abort('Aborting')

gradleTestRe = re.compile(r'^(\d+) tests completed, (\d+) failed$')

def getTestResult(testFilter: str, out: str, srcDir: str):
    out = out.replace('\r', '\n')
    buildDir = pjoin(srcDir, '..', '_build')
    testResultDir = pjoin(buildDir, 'test-results', 'test')
    tests = 0
    failures = 0
    errors = 0
    for file in ls(testResultDir, '*.xml'):
        tree = ET.parse(file)
        root = tree.getroot()
        if root.tag != 'testsuite':
            continue
        tests += int(root.get('tests', '0'))
        failures += int(root.get('skipped', '0'))
        failures += int(root.get('failures', '0'))
        errors += int(root.get('errors', '0'))
    if tests == 0:
        return TestResult(testFilter, out, True)
    else:
        return TestResult(testFilter, out, False, totalTests=tests, testFailures=failures, testErrors=errors)

def checkTest(assignment: Assignment, srcDir: str, testDir: str, testFilter: str, ctx: TestContext):
    debug(f'Running tests maching {testFilter} ...')
    result = execGradle('test', studentDir=srcDir, testDir=testDir, testFilter=testFilter)
    testResult = getTestResult(testFilter, result.stdout, srcDir)
    ctx.results.append(testResult)
    abortIfTestOkRequired(assignment, testResult)

def checkStyle(ctx: CheckCtx, srcDir: str, checkstylePath: str, config: str=checkstyleConfig):
    sourceFiles = []
    for root, dirs, files in os.walk(srcDir):
        for name in files:
            if name.lower().endswith('.java'):
               sourceFiles.append(os.path.join(root, name))
    cmd = [
        'java',
        '-cp',
        checkstylePath,
        '-Dbasedir=.',
        'com.puppycrawl.tools.checkstyle.Main',
        '-c',
        config,
    ]
    cmd += sourceFiles
    debug(f'Running "{cmd}"')
    result = run(cmd, onError='ignore', stderrToStdout=True, captureStdout=True)
    ctx.styleResult = StyleResult(hasErrors='ERROR' in result.stdout, styleOutput=result.stdout.replace('\r', '\n'))

def check(opts: JavaOptions):
    sheetDir = getSheetDir(opts.testDir, opts.sheet)
    exFile = pjoin(sheetDir, 'exercise.yaml')
    ex = parseExercise(opts.sheet, exFile)
    debug(f'Exercise (file: {exFile}): {ex}')
    # do the checks
    for a in ex.assignments:
        if not isFile(a.src):
            print(f'ERROR: File {a.src} not included in submission. I found the following .java files:')
            run('find . -name "*.java"')
    cp(defaultBuildFile, opts.sourceDir)
    srcDir = pjoin(opts.sourceDir, 'src')
    ctx = CheckCtx.empty('Compile')
    checkCompile(ctx, srcDir)
    testDir = pjoin(sheetDir, 'test-src')
    for a in ex.assignments:
        testCtx = TestContext(assignment=a, sheet=opts.sheet, results=[])
        ctx.tests.append(testCtx)
        for testFilter in a.tests:
            checkTest(a, srcDir, testDir, testFilter, testCtx)
    checkStyle(ctx, srcDir, opts.checkstylePath)
    outputResultsAndExit(ctx)
