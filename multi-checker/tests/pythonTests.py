from testUtils import *
import re

wyppDir = '/wypp/'

pythonTestDir = f'{praktomatTestsLocal}/python-prog1/'
python2TestDir = f'{praktomatTestsLocal}/python-prog2/'
localTestDir = f'{thisDir}/python-wypp'
styleTestDir = f'{localTestDir}/style'

# Some sample solutions in praktomat-tests are older than the coding conventions and violate them.
# The tests using them are not about the coding conventions, so they disable their check.
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

# Tests for the check of the coding conventions. Each submission in style/bad violates one rule (or the
# rules of one example of the style guide) and passes with the style check disabled.
# The list contains the problems the style check must report for aufgabe_01.py, as (line, code),
# and the beginnings of the violated style rules that must be shown.
namesRule = '- Names of functions'
typeNamesRule = '- Names of classes'
lineLengthRule = '- Lines have at most'
indentRule = '- Indent code'
parenRule = '- No space between the name'
bracketsRule = '- No space directly after'
commaColonRule = '- No space before but one space after'
operatorsRule = '- One space on both sides'
annotationsRule = '- All parameters'
badStyleTests: list[tuple[str, list[tuple[int, str]], list[str]]] = [
    ('naming-guide-example', [(6, 'invalid-name'), (7, 'invalid-name'), (8, 'invalid-name'),
                              (9, 'invalid-name'), (10, 'invalid-name'), (13, 'invalid-name')],
     [namesRule, typeNamesRule]),
    ('naming-uppercase', [(3, 'invalid-name'), (3, 'invalid-name'), (4, 'invalid-name')], [namesRule]),
    ('naming-type-alias', [(4, 'invalid-name')], [typeNamesRule]),
    ('naming-inconsistent', [(7, 'invalid-name')], [namesRule]),
    ('line-too-long', [(4, 'E501')], [lineLengthRule]),
    ('indent-guide-example', [(10, 'E111')], [indentRule]),
    ('indent-tabs', [(4, 'W191'), (5, 'W191')], [indentRule]),
    ('space-before-paren', [(6, 'E211')], [parenRule]),
    ('whitespace-guide-example', [(13, 'E225'), (13, 'E201'), (13, 'E201'), (13, 'E202'),
                                  (13, 'E201'), (13, 'E202'), (13, 'E231'), (13, 'E202')],
     [bracketsRule, commaColonRule, operatorsRule]),
    ('whitespace-comma-colon', [(3, 'E231'), (6, 'E231'), (7, 'E231'), (8, 'E203')], [commaColonRule]),
    ('whitespace-operators', [(3, 'E225'), (4, 'E225'), (6, 'E225'), (7, 'E225'), (9, 'E225')],
     [operatorsRule]),
    ('annotations-guide-example', [(5, 'ANN001'), (5, 'ANN201')], [annotationsRule]),
    ('annotations-missing-return', [(7, 'ANN201'), (10, 'ANN204'), (13, 'ANN201')], [annotationsRule]),
    ('annotations-missing-param', [(4, 'ANN001'), (7, 'ANN001'), (7, 'ANN002'), (7, 'ANN003'),
                                   (7, 'ANN201')], [annotationsRule]),
]

def styleCmd(extraArgs: str='') -> str:
    return f'python3 {checkScript} {checkScriptArgs} python --wypp {wyppDir} --sheet style {extraArgs}'

_styleIssueRe = re.compile(r'^(\S+\.py):(\d+):\d+: .* \[([\w-]+)\]$')

def conventionsOk(file: str) -> str:
    return f'## OK: {file} follows the coding conventions'

def conventionsViolated(file: str) -> str:
    return f'File {file} violates the coding conventions.'

def expectInOutput(res: RunResult, expected: list[str], notExpected: list[str]=[]):
    for s in expected:
        if s not in res.stdout:
            fail(f'expected "{s}" in output\n\n---\n{res.stdout}\n---')
    for s in notExpected:
        if s in res.stdout:
            fail(f'expected no "{s}" in output\n\n---\n{res.stdout}\n---')

def expectInOrder(res: RunResult, expected: list[str]):
    pos = 0
    for s in expected:
        i = res.stdout.find(s, pos)
        if i < 0:
            fail(f'expected "{s}" after position {pos} in output\n\n---\n{res.stdout}\n---')
        pos = i + len(s)

def expectStyleResult(res: RunResult, expected: list[str], issues: list[tuple[str, int, str]],
                      rules: list[str]=[]):
    """
    Checks that the output contains the expected strings, that it reports exactly the given
    violations of the coding conventions, as (file, line, code), and that it shows exactly the
    given rules.
    """
    expectInOutput(res, expected)
    found: list[tuple[str, int, str]] = []
    for l in res.stdout.split('\n'):
        m = _styleIssueRe.match(l)
        if m:
            found.append((m.group(1), int(m.group(2)), m.group(3)))
    if sorted(found) != sorted(issues):
        fail(f'expected style problems {sorted(issues)} but got {sorted(found)}\n\n---\n{res.stdout}\n---')
    shownRules = [l for l in res.stdout.split('\n') if l.startswith('- ')]
    if len(shownRules) != len(rules) or not all(any(l.startswith(r) for l in shownRules) for r in rules):
        fail(f'expected style rules {rules} but got {shownRules}\n\n---\n{res.stdout}\n---')

def expectNoStyleCheck(res: RunResult):
    expectInOutput(res, [], ['## Checking coding conventions', 'Coding conventions:'])

def test_python_style_good():
    for d in ['camel-case', 'snake-case', 'lenient']:
        print(d)
        res = expectOk(styleCmd(), external=f'{styleTestDir}/sheet', submissionDir=f'{styleTestDir}/good/{d}')
        expectStyleResult(res, [conventionsOk('aufgabe_01.py')], [])

def test_python_style_bad():
    for d, issues, rules in badStyleTests:
        print(d)
        res = expectFail(styleCmd(), 1, external=f'{styleTestDir}/sheet', submissionDir=f'{styleTestDir}/bad/{d}')
        expectStyleResult(res, [conventionsViolated('aufgabe_01.py'), 'Load and student tests status: FAIL'],
                          [('aufgabe_01.py', line, code) for (line, code) in issues], rules)

def test_python_style_disabled_by_option():
    for d, _, _ in badStyleTests:
        print(d)
        res = expectOk(styleCmd('--no-style-check'), external=f'{styleTestDir}/sheet',
                       submissionDir=f'{styleTestDir}/bad/{d}')
        expectNoStyleCheck(res)

def test_python_style_disabled_in_exercise_yaml():
    for d, _, _ in badStyleTests:
        print(d)
        res = expectOk(styleCmd(), external=f'{styleTestDir}/sheet-style-off',
                       submissionDir=f'{styleTestDir}/bad/{d}')
        expectNoStyleCheck(res)

def test_python_style_per_assignment():
    # The style check is disabled for assignment 1 (aufgabe_01.py) but not for assignment 2
    sheet = f'{styleTestDir}/sheet-per-assignment'
    res = expectOk(styleCmd(), external=sheet, submissionDir=f'{styleTestDir}/per-assignment/first-bad')
    expectStyleResult(res, [conventionsOk('aufgabe_02.py')], [])
    expectInOutput(res, [], ['## Checking coding conventions of aufgabe_01.py'])
    res = expectFail(styleCmd(), 1, external=sheet, submissionDir=f'{styleTestDir}/per-assignment/both-bad')
    expectStyleResult(res, [conventionsViolated('aufgabe_02.py')], [('aufgabe_02.py', 3, 'invalid-name')], [namesRule])
    expectInOutput(res, [], ['## Checking coding conventions of aufgabe_01.py'])

def test_python_style_without_exercise_yaml():
    res = expectOk(styleCmd('--assignment 1'), submissionDir=f'{styleTestDir}/good/camel-case')
    expectStyleResult(res, [conventionsOk('aufgabe_01.py')], [])
    bad = f'{styleTestDir}/bad/naming-guide-example'
    res = expectFail(styleCmd('--assignment 1'), 1, submissionDir=bad)
    expectStyleResult(res, [conventionsViolated('aufgabe_01.py'), 'aufgabe_01.py: failed'],
                      [('aufgabe_01.py', line, 'invalid-name') for line in [6, 7, 8, 9, 10, 13]],
                      [namesRule, typeNamesRule])
    res = expectOk(styleCmd('--assignment 1 --no-style-check'), submissionDir=bad)
    expectNoStyleCheck(res)

def test_python_style_per_file():
    # Each file is loaded first. Only if this succeeds, its coding conventions are checked, and a
    # violation makes the file fail. Then the next file follows. aufgabe_01.py does not load (its
    # violation of the conventions must not be reported), aufgabe_02.py violates the conventions,
    # aufgabe_03.py is OK.
    submission = f'{styleTestDir}/per-file'
    notExpected = ['## Checking coding conventions of aufgabe_01.py', 'Coding conventions:']
    issues = [('aufgabe_02.py', 3, 'E225')]
    # Without exercise.yaml
    res = expectFail(styleCmd('--assignment 1,2,3'), 1, submissionDir=submission)
    print(res.stdout)
    expectInOrder(res, ['Checking assignment 1', 'File aufgabe_01.py could not be loaded.',
                        'Checking assignment 2', '## OK: aufgabe_02.py loads successfully',
                        '## Checking coding conventions of aufgabe_02.py', conventionsViolated('aufgabe_02.py'),
                        'Checking assignment 3', '## OK: aufgabe_03.py loads successfully',
                        '## Checking coding conventions of aufgabe_03.py', conventionsOk('aufgabe_03.py'),
                        'Summary', 'aufgabe_01.py: failed', 'aufgabe_02.py: failed'])
    expectInOutput(res, [], notExpected + ['aufgabe_03.py: failed'])
    expectStyleResult(res, [], issues, [operatorsRule])
    # With exercise.yaml
    res = expectFail(styleCmd(), 1, external=f'{styleTestDir}/sheet-per-file', submissionDir=submission)
    print(res.stdout)
    expectInOrder(res, ['Load and student tests status: FAIL',
                        '## Checking that aufgabe_01.py loads successfully', 'File aufgabe_01.py could not be loaded.',
                        '## Checking that aufgabe_02.py loads successfully',
                        '## Checking coding conventions of aufgabe_02.py', conventionsViolated('aufgabe_02.py'),
                        '## Checking that aufgabe_03.py loads successfully',
                        '## Checking coding conventions of aufgabe_03.py', conventionsOk('aufgabe_03.py')])
    expectInOutput(res, [], notExpected)
    expectStyleResult(res, [], issues, [operatorsRule])

def test_python_style_command():
    # The python-style command only checks the coding conventions of the given files
    def cmd(files: str) -> str:
        return f'python3 {checkScript} {checkScriptArgs} python-style {files}'
    res = expectOk(cmd('aufgabe_01.py'), submissionDir=f'{styleTestDir}/good/camel-case')
    expectStyleResult(res, ['Coding conventions: OK'], [])
    res = expectFail(cmd('aufgabe_01.py aufgabe_02.py'), 1, submissionDir=f'{styleTestDir}/per-assignment/both-bad')
    expectStyleResult(res, ['Coding conventions: ERROR'],
                      [('aufgabe_01.py', 3, 'invalid-name'), ('aufgabe_02.py', 3, 'invalid-name')], [namesRule])
    # aufgabe_03.py has a syntax error, so it is not checked
    res = expectOk(cmd('aufgabe_01.py aufgabe_03.py'), submissionDir=localTestDir)
    expectStyleResult(res, ['Coding conventions: OK'], [])
    if 'aufgabe_03.py: coding conventions not checked because of syntax errors' not in res.stdout:
        fail(f'expected that aufgabe_03.py is not checked\n\n---\n{res.stdout}\n---')
    expectFail(cmd('aufgabe_03.py'), 1, submissionDir=localTestDir)
    expectFail(cmd('does_not_exist.py'), 1, submissionDir=localTestDir)

_styleIssueWithMessageRe = re.compile(r'^(\S+\.py):(\d+):(\d+): (.*) \[([\w-]+)\]$')

def test_python_style_german():
    # Checks all bad submissions at once in English and German: the same problems must be reported,
    # with translated messages, and all rules must be shown translated.
    files = ' '.join([f'{d}/aufgabe_01.py' for (d, _, _) in badStyleTests])
    def run(lang: str) -> tuple[RunResult, dict[tuple[str, int, int, str], list[str]], list[str]]:
        res = expectFail(f'python3 {checkScript} {checkScriptArgsNoLang} --lang {lang} python-style {files}', 1,
                         submissionDir=f'{styleTestDir}/bad')
        messages: dict[tuple[str, int, int, str], list[str]] = {}
        for l in res.stdout.split('\n'):
            m = _styleIssueWithMessageRe.match(l)
            if m:
                key = (m.group(1), int(m.group(2)), int(m.group(3)), m.group(5))
                messages.setdefault(key, []).append(m.group(4))
        rules = [l for l in res.stdout.split('\n') if l.startswith('- ')]
        return (res, messages, rules)
    (resEn, messagesEn, rulesEn) = run('en')
    (resDe, messagesDe, rulesDe) = run('de')
    if 'Programmierkonventionen: FEHLER' not in resDe.stdout:
        fail(f'expected "Programmierkonventionen: FEHLER" in output\n\n---\n{resDe.stdout}\n---')
    expectedCount = sum([len(issues) for (_, issues, _) in badStyleTests])
    if sum([len(ms) for ms in messagesEn.values()]) != expectedCount or messagesEn.keys() != messagesDe.keys():
        fail(f'expected the same {expectedCount} problems\n\n---\n{resEn.stdout}\n---\n{resDe.stdout}\n---')
    for key, msgsEn in messagesEn.items():
        for (en, de) in zip(sorted(msgsEn), sorted(messagesDe[key])):
            if en == de:
                fail(f'message not translated: {key} {en}')
    if len(rulesEn) != 9 or len(rulesDe) != 9 or any([en == de for (en, de) in zip(rulesEn, rulesDe)]):
        fail(f'expected 9 translated rules, got\n{rulesEn}\n{rulesDe}')

def test_python_wypp_lang():
    # WYPP runs in the language of the checker, given by --lang or by the locale. Its test results
    # are parsed in both languages.
    sheet = f'{localTestDir}/03'
    submission = f'{localTestDir}/03/solution-partial'
    english = ['Assignment 1: 1.0/3.0 points, 33% OK', 'Assignment 2: 1.0/3.0 points, 33% OK',
               'Tutor:  6 tests, 4 errors']
    german = ['Aufgabe 1: 1.0/3.0 Punkte, 33% OK', 'Aufgabe 2: 1.0/3.0 Punkte, 33% OK', 'Tutor:  6 Tests, 4 Fehler']
    for args, env, expected in [('--lang en', localeEnv(LANG='de_DE.UTF-8'), english),
                                ('--lang de', localeEnv(LANG='en_US.UTF-8'), german),
                                ('', localeEnv(LANG='de_DE.UTF-8'), german)]:
        res = expectFail(f'python3 {checkScript} {checkScriptArgsNoLang} {args} python --wypp {wyppDir} --sheet 03',
                         121, external=sheet, submissionDir=submission, env=env)
        for s in expected:
            if s not in res.stdout:
                fail(f'expected "{s}" in output\n\n---\n{res.stdout}\n---')

