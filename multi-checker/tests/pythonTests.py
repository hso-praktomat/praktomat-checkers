from testUtils import *
import re

wyppDir = '/wypp/'

pythonTestDir = f'{praktomatTestsLocal}/python-prog1/'
python2TestDir = f'{praktomatTestsLocal}/python-prog2/'
localTestDir = f'{thisDir}/python-wypp'
styleTestDir = f'{localTestDir}/style'

# Some sample solutions in praktomat-tests are older than the coding style guide and violate it.
# The tests using them are not about the coding style, so they disable the style check.
noStyleCheck = '--no-style-check'

def test_python01():
    expectOk(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 01 --assignment 1,4',
             submissionDir=localTestDir)

def test_python02():
    expectFail(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 01 --assignment 2',
               121, submissionDir=localTestDir)

def test_python03():
    expectFail(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 01 --assignment 2',
               121, submissionDir=localTestDir)

def test_python04():
    expectFail(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 01 --assignment 1,2',
               121, submissionDir=localTestDir)

def test_python05():
    expectFail(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 01 --assignment 3',
               1, submissionDir=localTestDir)

def test_python06():
    expectFail(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 01 --assignment 1,2,3',
               1, submissionDir=localTestDir)

def test_python07():
    pythonTests = [('solution-good', 0), ('solution-wrapped', 0), ('solution-partial', 121), ('solution-partial-missing', 121),
                ('solution-fail', 121), ('solution-error', 1), ('solution-with-own-test-errors', 121),
                ('solution-timeout', 1)]
    for d, ecode in pythonTests:
        print()
        print(d)
        sheetDirLocal = f'{praktomatCheckersLocal}/multi-checker/tests/python-wypp/03'
        submissionDir = f'{localTestDir}/03/{d}/'
        cmd = f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 03'
        env = {'PRAKTOMAT_CHECKER_TEST_TIMEOUT': '2'}
        if ecode == 0:
            res = expectOk(cmd, external=sheetDirLocal, submissionDir=submissionDir, env=env)
        else:
            res = expectFail(cmd, ecode, external=sheetDirLocal, submissionDir=submissionDir, env=env)
        if d == 'solution-timeout':
            if 'timeout' not in res.stdout.lower():
                fail(f'expected timeout in output\n\n---\n{res.stdout}\n---')

def test_python08():
    expectOk(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 09 {noStyleCheck}',
        external=f'{pythonTestDir}/09', submissionDir=f'{pythonTestDir}/09/solution/')

def test_python09():
    expectOk(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet labortest_2 {noStyleCheck}',
        external=f'{pythonTestDir}/labortest_2', submissionDir=f'{pythonTestDir}/labortest_2/solution/')

def test_python10():
    expectFail(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet labortest_2 {noStyleCheck}',
        121, external=f'{pythonTestDir}/labortest_2', submissionDir=f'{pythonTestDir}/labortest_2/solution-partial/')

def test_python11():
    expectFail(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet labortest_2',
        1, external=f'{pythonTestDir}/labortest_2', submissionDir=f'{pythonTestDir}/labortest_2/solution-nofiles/')

def test_python12():
    expectFail(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet abschlussprojekt',
        external=f'{pythonTestDir}/abschlussprojekt', submissionDir=f'{pythonTestDir}abschlussprojekt/solution-fail')

def test_python13():
    expectFail(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet abschlussprojekt',
        121, external=f'{pythonTestDir}/abschlussprojekt', submissionDir=f'{pythonTestDir}abschlussprojekt/solution-simple')

def test_python14():
    expectOk(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet abschlussprojekt',
        external=f'{pythonTestDir}/abschlussprojekt', submissionDir=f'{pythonTestDir}abschlussprojekt/solution')

def test_python15():
    expectOk(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 10-dicts-exceptions {noStyleCheck}',
        external=f'{pythonTestDir}/10-dicts-exceptions', submissionDir=f'{pythonTestDir}/solutions/10-dicts-exceptions')

def test_python16():
    expectOk(f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet 10-dicts-exceptions {noStyleCheck}',
        external=f'{pythonTestDir}/10-dicts-exceptions', submissionDir=f'{pythonTestDir}/solutions/10-dicts-exceptions/subdir')

def test_python17():
    prog2Sheets = ['P01-intro', 'P02-higher-order-funs', 'P03-OO', 'P04-Listen', 'P05-Sorting',
                'P06-Sorting2', 'P07-Design-Patterns', 'P08-Trees', 'P09-Functional-Iterator',
                'P11-Threads', 'P12-Hashing']
    prog2SheetsIncomplete = ['P01-intro', 'P06-Sorting2']
    prog2Sheets = ['P06-Sorting2']
    for s in prog2Sheets:
        cmd = f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet {s} {noStyleCheck}'
        external=f'{python2TestDir}/{s}'
        dir=f'{python2TestDir}{s}/solution'
        if s in prog2SheetsIncomplete:
            expectFail(cmd, external=external, submissionDir=dir, ecode=121)
        else:
            expectOk(cmd, external=external, submissionDir=dir)

# Tests for the coding style check. Each submission in style/bad violates exactly one rule of the
# style guide and passes with the style check disabled. The list contains the problems the
# style check must report for aufgabe_01.py, as (line, code).
badStyleTests: list[tuple[str, list[tuple[int, str]]]] = [
    ('naming-guide-example', [(6, 'invalid-name'), (7, 'invalid-name'), (8, 'invalid-name'),
                              (9, 'invalid-name'), (10, 'invalid-name'), (13, 'invalid-name')]),
    ('naming-uppercase', [(3, 'invalid-name'), (3, 'invalid-name'), (4, 'invalid-name')]),
    ('naming-type-alias', [(4, 'invalid-name')]),
    ('naming-inconsistent', [(7, 'invalid-name')]),
    ('line-too-long', [(4, 'E501')]),
    ('indent-guide-example', [(10, 'E111')]),
    ('indent-tabs', [(4, 'W191'), (5, 'W191')]),
    ('space-before-paren', [(6, 'E211')]),
    ('whitespace-guide-example', [(13, 'E225'), (13, 'E201'), (13, 'E201'), (13, 'E202'),
                                  (13, 'E201'), (13, 'E202'), (13, 'E231'), (13, 'E202')]),
    ('whitespace-comma-colon', [(3, 'E231'), (6, 'E231'), (7, 'E231'), (8, 'E203')]),
    ('whitespace-operators', [(3, 'E225'), (4, 'E225'), (6, 'E225'), (7, 'E225'), (9, 'E225')]),
    ('annotations-guide-example', [(5, 'ANN001'), (5, 'ANN201')]),
    ('annotations-missing-return', [(7, 'ANN201'), (10, 'ANN204'), (13, 'ANN201')]),
    ('annotations-missing-param', [(4, 'ANN001'), (7, 'ANN001'), (7, 'ANN002'), (7, 'ANN003'),
                                   (7, 'ANN201')]),
]

def styleCmd(extraArgs: str='') -> str:
    return f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet style {extraArgs}'

_styleIssueRe = re.compile(r'^(\S+\.py):(\d+):\d+: .* \[([\w-]+)\]$')

def expectStyleResult(res: RunResult, status: str, issues: list[tuple[str, int, str]]):
    """
    Checks the status of the style check in the summary and that the output reports exactly
    the given problems, as (file, line, code).
    """
    if f'Coding style: {status}' not in res.stdout:
        fail(f'expected "Coding style: {status}" in output\n\n---\n{res.stdout}\n---')
    found: list[tuple[str, int, str]] = []
    for l in res.stdout.split('\n'):
        m = _styleIssueRe.match(l)
        if m:
            found.append((m.group(1), int(m.group(2)), m.group(3)))
    if sorted(found) != sorted(issues):
        fail(f'expected style problems {sorted(issues)} but got {sorted(found)}\n\n---\n{res.stdout}\n---')

def expectNoStyleCheck(res: RunResult):
    if 'Coding style:' in res.stdout:
        fail(f'expected no style check\n\n---\n{res.stdout}\n---')

def test_python_style_good():
    for d in ['camel-case', 'snake-case', 'lenient']:
        print(d)
        res = expectOk(styleCmd(), external=f'{styleTestDir}/sheet', submissionDir=f'{styleTestDir}/good/{d}')
        expectStyleResult(res, 'OK', [])

def test_python_style_bad():
    for d, issues in badStyleTests:
        print(d)
        res = expectFail(styleCmd(), 1, external=f'{styleTestDir}/sheet', submissionDir=f'{styleTestDir}/bad/{d}')
        expectStyleResult(res, 'ERROR', [('aufgabe_01.py', line, code) for (line, code) in issues])

def test_python_style_disabled_by_option():
    for d, _ in badStyleTests:
        print(d)
        res = expectOk(styleCmd('--no-style-check'), external=f'{styleTestDir}/sheet',
                       submissionDir=f'{styleTestDir}/bad/{d}')
        expectNoStyleCheck(res)

def test_python_style_disabled_in_exercise_yaml():
    for d, _ in badStyleTests:
        print(d)
        res = expectOk(styleCmd(), external=f'{styleTestDir}/sheet-style-off',
                       submissionDir=f'{styleTestDir}/bad/{d}')
        expectNoStyleCheck(res)

def test_python_style_per_assignment():
    # The style check is disabled for assignment 1 (aufgabe_01.py) but not for assignment 2
    sheet = f'{styleTestDir}/sheet-per-assignment'
    res = expectOk(styleCmd(), external=sheet, submissionDir=f'{styleTestDir}/per-assignment/first-bad')
    expectStyleResult(res, 'OK', [])
    res = expectFail(styleCmd(), 1, external=sheet, submissionDir=f'{styleTestDir}/per-assignment/both-bad')
    expectStyleResult(res, 'ERROR', [('aufgabe_02.py', 3, 'invalid-name')])

def test_python_style_without_exercise_yaml():
    res = expectOk(styleCmd('--assignment 1'), submissionDir=f'{styleTestDir}/good/camel-case')
    expectStyleResult(res, 'OK', [])
    bad = f'{styleTestDir}/bad/naming-guide-example'
    res = expectFail(styleCmd('--assignment 1'), 1, submissionDir=bad)
    expectStyleResult(res, 'ERROR', [('aufgabe_01.py', line, 'invalid-name') for line in [6, 7, 8, 9, 10, 13]])
    res = expectOk(styleCmd('--assignment 1 --no-style-check'), submissionDir=bad)
    expectNoStyleCheck(res)
    # Both assignments refer to aufgabe_01.py, its problems must be reported only once
    res = expectFail(styleCmd('--assignment 1,01'), 1, submissionDir=bad)
    expectStyleResult(res, 'ERROR', [('aufgabe_01.py', line, 'invalid-name') for line in [6, 7, 8, 9, 10, 13]])

def test_python_style_command():
    # The python-style command only checks the coding style of the given files
    def cmd(files: str) -> str:
        return f'python3 {checkScript} {checkScriptArgs} python-style {files}'
    res = expectOk(cmd('aufgabe_01.py'), submissionDir=f'{styleTestDir}/good/camel-case')
    expectStyleResult(res, 'OK', [])
    res = expectFail(cmd('aufgabe_01.py aufgabe_02.py'), 1, submissionDir=f'{styleTestDir}/per-assignment/both-bad')
    expectStyleResult(res, 'ERROR', [('aufgabe_01.py', 3, 'invalid-name'), ('aufgabe_02.py', 3, 'invalid-name')])
    # aufgabe_03.py has a syntax error, so it is not checked
    res = expectOk(cmd('aufgabe_01.py aufgabe_03.py'), submissionDir=localTestDir)
    expectStyleResult(res, 'OK', [])
    if 'aufgabe_03.py: coding style not checked because of syntax errors' not in res.stdout:
        fail(f'expected that aufgabe_03.py is not checked\n\n---\n{res.stdout}\n---')
    expectFail(cmd('aufgabe_03.py'), 1, submissionDir=localTestDir)
    expectFail(cmd('does_not_exist.py'), 1, submissionDir=localTestDir)

