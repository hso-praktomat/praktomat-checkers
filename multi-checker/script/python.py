from dataclasses import dataclass
from typing import Optional
from shell import *
import sys
import os
from utils import *
from common import *

@dataclass
class PythonOptions(Options):
    assignment: str
    wypp: str

def runWypp(studentFile, flag, opts):
    wyppPath = opts.wypp
    env = {'PYTHONPATH': wyppPath + '/python/src:' + wyppPath + '/python/site-lib'}
    print()
    res = run(['python3', wyppPath + '/python/src/runYourProgram.py', flag, studentFile],
              onError='ignore', env=env)
    print()
    return (res.exitcode == 0)

def check(opts: Options):
    p = f'aufgabe_{opts.assignment.zfill(2)}.py'
    studentFile = findFile(p, opts.sourceDir)
    if not studentFile:
        pyFilesList = run(f'find {opts.sourceDir} -name "*.py"', captureStdout=splitLines, onError='ignore').stdout
        pyFiles = '\n'.join(pyFilesList)
        print(f'''FEHLER: Datei {p} nicht in Abgabe enthalten.

Folgende Dateien mit der Endung .py wurden gefunden:

{pyFiles}''')
        sys.exit(OK_WITH_WARNINGS_EXIT_CODE)
    fixEncoding(studentFile)
    print()
    print(f'## Überprüfe dass {p} beim Laden keinen Fehler verursacht ...')
    runRes = runWypp(studentFile, '--check-runnable', opts)
    if runRes:
        print(f'## OK: {p} erfolgreich geladen')
    else:
        abort(f'''Datei {p} konnte nicht geladen werden.
Weiter oben finden Sie die Fehlermeldungen.''')
    print()
    print(f'## Führe Tests in {p} aus ...')
    testRes = runWypp(studentFile, '--check', opts)
    if testRes:
        print(f'## OK: keine Testfehler in {p}')
    else:
        abort(f'''Datei {p} enthält fehlerhafte Tests
Falls Sie einen Test nicht zum Laufen bringen, müssen
Sie diesen Test auskommentieren.''')
