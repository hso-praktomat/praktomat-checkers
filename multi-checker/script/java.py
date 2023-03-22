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

GRADLE_OFFLINE = True # Should be True

# Checking Java code using Gradle

@dataclass
class JavaOptions(Options):
    sheet: str
    checkstylePath: str

defaultBuildFile = pjoin(os.path.realpath(os.path.dirname(__file__)), 'build.gradle.kts')
checkstyleConfig = pjoin(os.path.realpath(os.path.dirname(__file__)), 'checkstyle.xml')

def execGradle(task: str, studentDir: str, testDir: str='test-src', testFilter: str='*'):
    buildFile = abspath(pjoin(studentDir, '..', 'build.gradle.kts'))
    cmd = [
        'gradle',
        '-b',
        buildFile,
        '-PtestFilter=' + testFilter,
        '-PtestDir=' + testDir,
        '-PstudentDir=' + studentDir,
        task,
        '--no-parallel',
        '--max-workers=1',
        '--warning-mode=none',
        '-Dorg.gradle.welcome=never'
    ]
    if GRADLE_OFFLINE:
        cmd.append('--offline')
    debug(f'Running "{cmd}"')
    result = run(cmd, onError='ignore', stderrToStdout=True, captureStdout=True)
    return result

def checkCompile(ctx: CheckCtx, srcDir: str, exResult: CompileStatus):
    result = execGradle('compileJava', studentDir=srcDir)
    out = result.stdout
    if result.exitcode == 0:
        ctx.compileOutput = out
        ctx.compileStatus = exResult
    else:
        print(f'Compiling failed\n\n{out}')
        findOut = run('find . -type f | xargs ls -l', onError='ignore', stderrToStdout=True, captureStdout=True).stdout
        debug(f'Directory listing:\n{findOut}')
        abort('Aborting')

gradleTestRe = re.compile(r'^(\d+) tests completed, (\d+) failed$')

def getTestResult(testFilter: str, exitCode: int, out: str, srcDir: str):
    out = out.replace('\r', '\n')
    testResultDir = abspath(pjoin(srcDir, '..', '_build', 'test-results', 'test'))
    tests = 0
    failures = 0
    errors = 0
    if exitCode == 0:
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
            return TestResult(testFilter, out, False, totalTests=tests,
                              testFailures=failures, testErrors=errors)
    else:
        return TestResult(testFilter, out, False)

def checkTest(assignment: Assignment, srcDir: str, testDir: str, testFilter: str, ctx: TestContext):
    debug(f'Running tests maching {testFilter} ...')
    result = execGradle('test', studentDir=srcDir, testDir=testDir, testFilter=testFilter)
    testResult = getTestResult(testFilter, result.exitcode, result.stdout, srcDir)
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
    hasErrors = 'ERROR' in result.stdout or result.exitcode != 0
    if hasErrors:
        print('Checking code style FAILED')
        print()
        print(result.stdout)
        print()
        print('Here are the style rules to follow:')
        print('- Naming conventions')
        print('  - All identifiers except for constants in camel case, do not use underscores to separate words')
        print('  - Names of classes, interfaces, records and enums start with an uppercase letters')
        print('  - Names of methods and variables start with a lowercase letter')
        print('  - Names of constants are written in SCREAMING_CASE')
        print('- Indentation')
        print('  - Indent a block with four spaces')
        print('  - Do NOT use tabs, this might require to change the settings of your IDE')
        print()
        abort('Aborting')
    ctx.styleResult = StyleResult(hasErrors=hasErrors, styleOutput=result.stdout.replace('\r', '\n'))

def checkFilesExist(ex: Exercise, prjDir: str):
    missing = 0
    for a in ex.assignments:
        srcFile = pjoin(prjDir, a.src)
        if not isFile(srcFile):
            print(f'ERROR: File {srcFile} not included in submission.')
            missing = missing + 1
    if missing > 0:
        print(f'I found the following .java files:')
        run(f'find {prjDir} -name "*.java"')
        if missing == len(ex.assignments):
            abort('All files missing, aborting')
        return 'OK_BUT_SOME_MISSING'
    else:
        return 'OK'

def check(opts: JavaOptions):
    sheetDir = getSheetDir(opts.testDir, opts.sheet)
    exFile = pjoin(sheetDir, 'exercise.yaml')
    ex = parseExercise(opts.sheet, exFile)
    debug(f'Exercise (file: {exFile}): {ex}')
    ctx = CheckCtx.empty('Compile')
    # do the checks
    projectDir = opts.sourceDir
    for pDir in ls(opts.sourceDir):
        if not isDir(pDir):
            continue
        for entry in ls(pDir):
            if entry.endswith('src'):
                projectDir = pDir
    debug(f'projectDir={projectDir}')
    cp(defaultBuildFile, projectDir)
    srcDir = pjoin(projectDir, 'src')
    exResult = checkFilesExist(ex, projectDir)
    checkStyle(ctx, srcDir, opts.checkstylePath)
    checkCompile(ctx, srcDir, exResult)
    testDir = pjoin(sheetDir, 'test-src')
    for a in ex.assignments:
        testCtx = TestContext(assignment=a, sheet=opts.sheet, results=[])
        ctx.tests.append(testCtx)
        for testFilter in a.tests:
            checkTest(a, srcDir, testDir, testFilter, testCtx)
    outputResultsAndExit(ctx)
