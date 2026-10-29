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
from i18n import tr, trKey
import ast
import json
import os
import re
import string
import sys

styleConfigDir = pjoin(os.path.realpath(os.path.dirname(__file__)), 'python-style')

# Timeout in seconds for each of the style checkers. Independent of testTimeoutSeconds(),
# because the tests set the test timeout to 2 seconds.
styleCheckTimeout = 60

maxIssuesPerFile = 30

@dataclass(frozen=True)
class StyleRule:
    description: str   # English, translated when shown
    # Prefixes of the codes of ruff for this rule. The naming rules are checked by pylint.
    codePrefixes: tuple[str, ...]

namesRule = StyleRule(trKey(
    '- Names of functions, methods, parameters, variables and attributes start with a lowercase letter\n'
    '  and use camelCase. snake_case is also allowed, but use only one of the two styles in a file.'), ())
typeNamesRule = StyleRule(trKey(
    '- Names of classes, records and types (Literal, Union) start with an uppercase letter and use\n'
    '  CamelCase.'), ())

# The rules of the style guide that are checked, in the order of the style guide
styleRules = [
    namesRule,
    typeNamesRule,
    StyleRule(trKey('- Lines have at most 120 characters.'), ('E501',)),
    StyleRule(trKey('- Indent code with 4 spaces, do NOT use tabs. '
                    'This might require to change the settings of your editor.'), ('E11', 'W191')),
    StyleRule(trKey('- No space between the name of a function and the opening parenthesis: doSomething()'),
              ('E211',)),
    StyleRule(trKey('- No space directly after an opening or before a closing bracket: spam(ham[1], {eggs: 2})'),
              ('E201', 'E202')),
    StyleRule(trKey('- No space before but one space after a comma or a colon: f(a, b), {eggs: 2}, x: int'),
              ('E203', 'E231')),
    StyleRule(trKey('- One space on both sides of =, ==, +=, <, <=, -> and other operators: x = y, def f() -> int'),
              ('E225',)),
    StyleRule(trKey('- All parameters (except self) and the results of functions and methods have type '
                    'annotations:\n  def calculateSomething(param: int) -> float'), ('ANN',)),
]

def ruleForCode(code: str) -> Optional[StyleRule]:
    for r in styleRules:
        if any(code.startswith(p) for p in r.codePrefixes):
            return r
    return None

@dataclass
class StyleIssue:
    path: str
    line: int
    column: int
    code: str
    message: str
    rule: Optional[StyleRule]   # None if unknown
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

# The messages of ruff for the selected codes, with placeholders for their parameters. ruff has only
# English messages, so they are translated with these templates. A message that does not match
# (e.g. after an update of ruff) is shown in English.
_ruffMessages: dict[str, list[str]] = {
    'E501': [trKey('Line too long ({width} > {limit})')],
    'E111': [trKey('Indentation is not a multiple of {indentWidth}')],
    'E117': [trKey('Over-indented'), trKey('Over-indented (comment)')],
    'W191': [trKey('Indentation contains tabs')],
    'E211': [trKey("Whitespace before '{symbol}'")],
    'E201': [trKey("Whitespace after '{symbol}'")],
    'E202': [trKey("Whitespace before '{symbol}'")],
    'E203': [trKey("Whitespace before '{symbol}'")],
    'E225': [trKey('Missing whitespace around operator')],
    'E231': [trKey('Missing whitespace after {symbol}')],
    'ANN001': [trKey('Missing type annotation for function argument `{name}`')],
    'ANN002': [trKey('Missing type annotation for `*{name}`')],
    'ANN003': [trKey('Missing type annotation for `**{name}`')],
    'ANN201': [trKey('Missing return type annotation for public function `{name}`')],
    'ANN202': [trKey('Missing return type annotation for private function `{name}`')],
    'ANN204': [trKey('Missing return type annotation for special method `{name}`')],
    'ANN205': [trKey('Missing return type annotation for staticmethod `{name}`')],
    'ANN206': [trKey('Missing return type annotation for classmethod `{name}`')],
}

def _templateRegex(template: str) -> re.Pattern[str]:
    parts: list[str] = []
    for (literal, field, _, _) in string.Formatter().parse(template):
        parts.append(re.escape(literal))
        if field is not None:
            parts.append(f'(?P<{field}>.+?)')
    return re.compile(''.join(parts))

def ruffMessage(code: str, msg: str) -> str:
    for template in _ruffMessages.get(code, []):
        m = _templateRegex(template).fullmatch(msg)
        if m:
            return tr(template, **m.groupdict())
    return msg

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
        issues.append(StyleIssue(os.path.relpath(path), loc['row'], loc['column'], code, ruffMessage(code, msg),
                                 ruleForCode(code)))
    return issues

# Message of pylint for invalid-name, e.g.
#   Function name "do_Nothing" doesn't conform to '(?:(?P<exempt>...' pattern
#   Function name "foo_bar" doesn't conform to the `camel` group in the '(?:(?P<exempt>...' pattern
_pylintNameRe = re.compile(r'^(?P<kind>.+?) name "(?P<name>.*)" doesn\'t conform to (?:the `(?P<group>\w+)` group)?')
_nameKinds: dict[str, str] = {
    'Function': trKey('Function name "{name}"'),
    'Method': trKey('Method name "{name}"'),
    'Argument': trKey('Parameter name "{name}"'),
    'Variable': trKey('Variable name "{name}"'),
    'Constant': trKey('Variable name "{name}"'),
    'Inline iteration': trKey('Variable name "{name}"'),
    'Attribute': trKey('Attribute name "{name}"'),
    'Class attribute': trKey('Attribute name "{name}"'),
    'Class': trKey('Class name "{name}"'),
    'Type alias': trKey('Type alias name "{name}"'),
    'Type variable': trKey('Type variable name "{name}"'),
}
_upperCaseKinds = ['Class', 'Type alias', 'Type variable']
_groupStyles = {'camel': 'camelCase', 'snake': 'snake_case'}

def namingMessage(pylintMsg: str) -> tuple[str, Optional[StyleRule]]:
    """
    Returns a message for students and the violated rule.
    """
    m = _pylintNameRe.match(pylintMsg)
    if not m:
        return (pylintMsg, None)
    kind = m.group('kind')
    name = m.group('name')
    group = m.group('group')
    kindTemplate = _nameKinds.get(kind)
    what = tr(kindTemplate, name=name) if kindTemplate else f'{kind} name "{name}"'
    if group in _groupStyles:
        otherGroup = 'snake' if group == 'camel' else 'camel'
        return (tr('{what} is in {style}, but most names in this file are in {mainStyle}', what=what,
                   style=_groupStyles[otherGroup], mainStyle=_groupStyles[group]), namesRule)
    elif kind in _upperCaseKinds:
        return (tr('{what} does not follow the naming conventions: use CamelCase, starting with an uppercase '
                   'letter', what=what), typeNamesRule)
    else:
        return (tr('{what} does not follow the naming conventions: use camelCase or snake_case, starting with '
                   'a lowercase letter', what=what), namesRule)

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
        (msg, rule) = namingMessage(d['message'])
        # pylint counts columns from 0, ruff from 1
        issues.append(StyleIssue(os.path.relpath(path), d['line'], d['column'] + 1, d['symbol'], msg, rule))
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
            out.append(tr('{file}: coding style not checked because of syntax errors', file=f))
    if not checkedFiles:
        return None
    out.insert(0, tr('Checking coding style of {files}', files=', '.join(checkedFiles)) + '\n')
    issues = runRuff(checkedFiles) + runPylint(checkedFiles)
    issues.sort(key=lambda i: (i.path, i.line, i.column, i.code))
    if not issues:
        out.append(tr('No problems with the coding style found.'))
        return StyleResult(hasErrors=False, styleOutput='\n'.join(out))
    issuesPerFile: dict[str, int] = {}
    for i in issues:
        n = issuesPerFile.get(i.path, 0) + 1
        issuesPerFile[i.path] = n
        if n <= maxIssuesPerFile:
            out.append(i.format())
    for path, n in issuesPerFile.items():
        if n > maxIssuesPerFile:
            out.append(tr('... and {n} more problems in {file}', n=n - maxIssuesPerFile, file=path))
    out.append('')
    out.append(tr('Found {n} problem(s) with the coding style.', n=len(issues)))
    out.append('')
    # Show only the violated rules, or all rules if the rule of some problem is unknown
    violated = set([i.rule for i in issues])
    rules = styleRules if None in violated else [r for r in styleRules if r in violated]
    out.append(tr('Please follow these rules of the coding style guide:'))
    for r in rules:
        out.append(tr(r.description))
    return StyleResult(hasErrors=True, styleOutput='\n'.join(out))

def checkStyleAndExit(files: list[str]) -> NoReturn:
    """
    Implements the python-style command: checks the coding style of the given files, prints
    the result and exits with 0 if there are no problems, and with 1 otherwise.
    """
    for f in files:
        if not isFile(f):
            abort(tr('File {file} does not exist', file=f))
    res = checkStyle(files)
    if res is None:
        abort(tr('Coding style not checked, because all files contain syntax errors'))
    print(res.styleOutput)
    print('\n' + tr('Coding style: {status}', status=res.status))
    sys.exit(1 if res.hasErrors else 0)
