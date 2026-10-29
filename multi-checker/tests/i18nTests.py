from testUtils import *
import ast
import string
import sys

# Tests for the language of the messages (English or German)

scriptDir = f'{praktomatCheckersLocal}/multi-checker/script'
sys.path.append(scriptDir)
import i18n

def _formatFields(s: str) -> list[str]:
    return sorted([f for (_, f, _, _) in string.Formatter().parse(s) if f is not None])

def _translationKeys() -> list[str]:
    """
    Returns the string literals passed to tr and trKey in the checker scripts.
    """
    keys: list[str] = []
    for p in ls(scriptDir, '*.py'):
        tree = ast.parse(readFile(p), filename=p)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in ['tr', 'trKey'] and node.args):
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                keys.append(arg.value)
            elif node.func.id == 'trKey' or isinstance(arg, ast.JoinedStr):
                # tr may get a variable with a message marked by trKey, but no f-string
                fail(f'{p}:{node.lineno}: {node.func.id} needs a string literal')
    return keys

def test_translations_complete():
    keys = set(_translationKeys())
    if len(keys) < 100:
        fail(f'expected at least 100 messages, found only {len(keys)}')
    missing = sorted(keys - set(i18n.DE))
    if missing:
        fail('Missing German translations:\n' + '\n'.join(missing))
    unused = sorted(set(i18n.DE) - keys)
    if unused:
        fail('Unused German translations:\n' + '\n'.join(unused))
    for k in keys:
        if _formatFields(k) != _formatFields(i18n.DE[k]):
            fail(f'German translation has other placeholders than the English message:\n{k}\n{i18n.DE[k]}')

# The language is selected as in WYPP: commandline option --lang, then the locale, then English.
def outputLang(args: str, env: dict[str, str]) -> str:
    cmd = f'python3 {checkScript} {checkScriptArgsNoLang} {args}'
    res = expectOk(cmd, submissionDir=f'{thisDir}/python-wypp/style/good/camel-case', env=env)
    if 'Coding conventions: OK' in res.stdout:
        return 'en'
    if 'Programmierkonventionen: OK' in res.stdout:
        return 'de'
    fail(f'unknown language of output\n\n---\n{res.stdout}\n---')

def test_lang_from_locale():
    # The examples from the description of WYPP. LANGUAGE and LC_MESSAGES do not count, because
    # Python sets LC_CTYPE from the environment at startup.
    tests = [
        (localeEnv(), 'en'),
        (localeEnv(LANG='de_DE.UTF-8'), 'de'),
        (localeEnv(LC_ALL='de_DE.UTF-8'), 'de'),
        (localeEnv(LC_CTYPE='de_DE.UTF-8', LANG='en_US.UTF-8'), 'de'),
        (localeEnv(LANG='en_US.UTF-8', LANGUAGE='de'), 'en'),
        (localeEnv(LC_MESSAGES='de_DE.UTF-8', LANG='en_US.UTF-8'), 'en'),
        (localeEnv(LANG='C', LANGUAGE='de'), 'en'),
    ]
    for env, lang in tests:
        print(env)
        l = outputLang('python-style aufgabe_01.py', env)
        if l != lang:
            fail(f'expected language {lang} for {env}, got {l}')

def test_lang_option():
    # --lang comes before the locale, before or after the command
    for args, env, lang in [('--lang en python-style aufgabe_01.py', localeEnv(LANG='de_DE.UTF-8'), 'en'),
                            ('--lang de python-style aufgabe_01.py', localeEnv(LANG='en_US.UTF-8'), 'de'),
                            ('python-style --lang de aufgabe_01.py', localeEnv(), 'de')]:
        print(args)
        l = outputLang(args, env)
        if l != lang:
            fail(f'expected language {lang} for {args}, got {l}')
    expectFail(f'python3 {checkScript} {checkScriptArgsNoLang} --lang fr python-style aufgabe_01.py', 1,
               submissionDir=f'{thisDir}/python-wypp/style/good/camel-case')
