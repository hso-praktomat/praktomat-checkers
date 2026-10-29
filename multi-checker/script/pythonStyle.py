# Checking the coding style of python submissions with ruff and pylint.
# The rules come from the coding style guide of the course; python-style/ruff.toml and
# python-style/pylintrc explain which rules are checked by which tool.
from __future__ import annotations
from dataclasses import dataclass
from typing import *
from shell import *
from utils import *
from common import *
from testContext import StyleResult
import ast
import json
import os
import re
import sys

styleConfigDir = pjoin(os.path.realpath(os.path.dirname(__file__)), 'python-style')

# Timeout in seconds for each of the style checkers. Independent of testTimeoutSeconds(),
# because the tests set the test timeout to 2 seconds.
styleCheckTimeout = 60

maxIssuesPerFile = 30

styleRules = '''Please follow the coding style guide. These are the rules that are checked automatically:
- Names of functions, methods, parameters, variables and attributes start with a lowercase letter
  and use camelCase. snake_case is also allowed, but use only one of the two styles in a file.
- Names of classes, records and types (Literal, Union) start with an uppercase letter and use
  CamelCase.
- Lines have at most 120 characters.
- Indent code with 4 spaces, do NOT use tabs. This might require to change the settings of your editor.
- No space between the name of a function and the opening parenthesis: doSomething()
- No space directly after an opening or before a closing bracket: spam(ham[1], {eggs: 2})
- No space before but one space after a comma or a colon: f(a, b), {eggs: 2}, x: int
- One space on both sides of =, ==, +=, <, <=, -> and other operators: x = y, def f() -> int
- All parameters (except self) and the results of functions and methods have type annotations:
  def calculateSomething(param: int) -> float'''

@dataclass
class StyleIssue:
    path: str
    line: int
    column: int
    code: str
    message: str
    def format(self) -> str:
        return f'{self.path}:{self.line}:{self.column}: {self.message} [{self.code}]'

def hasValidSyntax(path: str) -> bool:
    try:
        ast.parse(readFile(path), filename=path)
        return True
    except (SyntaxError, ValueError, UnicodeDecodeError):
        return False

def runStyleChecker(args: list[str]) -> RunResult:
    cmd = [sys.executable, '-m'] + args
    debug(f'Running {cmd}')
    res = run(cmd, onError='ignore', captureStdout=True, captureStderr=True, timeout=styleCheckTimeout)
    debug(f'Exit code: {res.exitcode}\nStdout:\n{res.stdout}\nStderr:\n{res.stderr}')
    if res.exitcode == TIMEOUT_EXIT_CODE:
        bug(f'Timeout after {styleCheckTimeout}s while checking the coding style with {args[0]}')
    return res

def parseJson(what: str, res: RunResult) -> list[dict[str, Any]]:
    try:
        return cast(list[dict[str, Any]], json.loads(res.stdout))
    except json.JSONDecodeError:
        bug(f'{what} failed with exit code {res.exitcode}:\n{res.stdout}\n{res.stderr}')

def runRuff(files: list[str]) -> list[StyleIssue]:
    res = runStyleChecker(['ruff', 'check', '--config', pjoin(styleConfigDir, 'ruff.toml'), '--no-cache',
                           '--output-format=json'] + files)
    # Exit code 1 means that ruff found problems, 2 means that ruff failed
    if res.exitcode not in [0, 1]:
        bug(f'ruff failed with exit code {res.exitcode}:\n{res.stdout}\n{res.stderr}')
    issues: list[StyleIssue] = []
    for d in parseJson('ruff', res):
        code = d['code']
        msg = d['message']
        if code is None:
            # syntax error, files with syntax errors are not checked
            continue
        if code == 'ANN204' and '`__init__`' in msg:
            # Lenient: __init__ needs no return type annotation
            continue
        path: str = d['filename']
        loc = d['location']
        issues.append(StyleIssue(os.path.relpath(path), loc['row'], loc['column'], code, msg))
    return issues

# Message of pylint for invalid-name, e.g.
#   Function name "do_Nothing" doesn't conform to '(?:(?P<exempt>...' pattern
#   Function name "foo_bar" doesn't conform to the `camel` group in the '(?:(?P<exempt>...' pattern
_pylintNameRe = re.compile(r'^(?P<kind>.+?) name "(?P<name>.*)" doesn\'t conform to (?:the `(?P<group>\w+)` group)?')
_kindNames = {'Argument': 'Parameter', 'Class attribute': 'Attribute', 'Constant': 'Variable',
              'Inline iteration': 'Variable'}
_upperCaseKinds = ['Class', 'Type alias', 'Type variable']
_groupStyles = {'camel': 'camelCase', 'snake': 'snake_case'}

def namingMessage(pylintMsg: str) -> str:
    m = _pylintNameRe.match(pylintMsg)
    if not m:
        return pylintMsg
    kind = m.group('kind')
    name = m.group('name')
    group = m.group('group')
    what = f'{_kindNames.get(kind, kind)} name "{name}"'
    if group in _groupStyles:
        otherGroup = 'snake' if group == 'camel' else 'camel'
        return f'{what} is in {_groupStyles[otherGroup]}, but most names in this file are in ' \
            f'{_groupStyles[group]}'
    elif kind in _upperCaseKinds:
        return f'{what} does not follow the naming conventions: use CamelCase, starting with an uppercase letter'
    else:
        return f'{what} does not follow the naming conventions: use camelCase or snake_case, starting with ' \
            'a lowercase letter'

def runPylint(files: list[str]) -> list[StyleIssue]:
    res = runStyleChecker(['pylint', '--rcfile', pjoin(styleConfigDir, 'pylintrc'), '--output-format=json']
                          + files)
    # The exit code of pylint is a bit mask, 32 means usage error. Fatal errors (1) for some file,
    # e.g. a crash of pylint, are ignored, because in doubt the style check is lenient.
    if res.exitcode < 0 or res.exitcode & 32:
        bug(f'pylint failed with exit code {res.exitcode}:\n{res.stdout}\n{res.stderr}')
    issues: list[StyleIssue] = []
    for d in parseJson('pylint', res):
        if d['symbol'] != 'invalid-name':
            debug(f'Ignoring pylint message {d}')
            continue
        path: str = d['path']
        # pylint counts columns from 0, ruff from 1
        issues.append(StyleIssue(os.path.relpath(path), d['line'], d['column'] + 1, d['symbol'],
                                 namingMessage(d['message'])))
    return issues

def checkStyle(files: list[str]) -> Optional[StyleResult]:
    """
    Checks the coding style of the given files. Files with syntax errors are not checked,
    their errors are reported when loading them. Returns None if no file was checked.
    Executed from within the source dir.
    """
    out: list[str] = []
    checkedFiles: list[str] = []
    for f in files:
        f = os.path.relpath(f)
        if hasValidSyntax(f):
            checkedFiles.append(f)
        else:
            out.append(f'{f}: coding style not checked because of syntax errors')
    if not checkedFiles:
        return None
    out.insert(0, f'Checking coding style of {", ".join(checkedFiles)}\n')
    issues = runRuff(checkedFiles) + runPylint(checkedFiles)
    issues.sort(key=lambda i: (i.path, i.line, i.column, i.code))
    if not issues:
        out.append('No problems with the coding style found.')
        return StyleResult(hasErrors=False, styleOutput='\n'.join(out))
    issuesPerFile: dict[str, int] = {}
    for i in issues:
        n = issuesPerFile.get(i.path, 0) + 1
        issuesPerFile[i.path] = n
        if n <= maxIssuesPerFile:
            out.append(i.format())
    for path, n in issuesPerFile.items():
        if n > maxIssuesPerFile:
            out.append(f'... and {n - maxIssuesPerFile} more problems in {path}')
    out.append('')
    out.append(f'Found {len(issues)} problem(s) with the coding style.')
    out.append('')
    out.append(styleRules)
    return StyleResult(hasErrors=True, styleOutput='\n'.join(out))

def checkStyleAndExit(files: list[str]) -> NoReturn:
    """
    Implements the python-style command: checks the coding style of the given files, prints
    the result and exits with 0 if there are no problems, and with 1 otherwise.
    """
    for f in files:
        if not isFile(f):
            abort(f'File {f} does not exist')
    res = checkStyle(files)
    if res is None:
        abort('Coding style not checked, because all files contain syntax errors')
    print(res.styleOutput)
    print(f'\nCoding style: {res.status}')
    sys.exit(1 if res.hasErrors else 0)
