from dataclasses import dataclass
from typing import Optional
from shell import *
import sys
import os

FILE_NOT_FOUND_EXIT_CODE = 121

@dataclass
class Options:
    exerciseNo: str

def abort(msg: str):
    print('FEHLER: ' + msg)
    sys.exit(1)

# wyppPath = '/Users/swehr/devel/write-your-python-program'
wyppPath = '/wypp'

# Adapted from https://github.com/skogsbaer/check-assignments/blob/main/src/fixEncodingCmd.py
replacements = ['ä', 'ö', 'ü', 'Ä', 'Ö', 'Ü', 'ß']
def fixEncoding(path):
    bytes_orig = open(path, 'rb').read()
    bytes = bytes_orig
    for r in replacements:
        bytes = bytes.replace(r.encode('iso-8859-1'), r.encode('utf-8'))
    if bytes != bytes_orig:
        open(path, 'wb').write(bytes)
        print(f'Fixed encoding of {path}')

def findFile(p: str) -> Optional[str]:
    if isFile(p):
        return p
    for x in ls('.'):
        if isDir(x):
            cand = pjoin(x, p)
            if isFile(cand):
                return cand
    return None

def runWypp(studentFile, flag):
    env = {'PYTHONPATH': wyppPath + '/python/src:' + wyppPath + '/python/site-lib'}
    print()
    res = run(['python3', wyppPath + '/python/src/runYourProgram.py', flag, studentFile],
              onError='ignore', env=env)
    print()
    return (res.exitcode == 0)

def main(opts: Options):
    p = f'aufgabe_{opts.exerciseNo.zfill(2)}.py'
    studentFile = findFile(p)
    if not studentFile:
        pyFilesList = run('find . -name "*.py"', captureStdout=splitLines, onError='ignore').stdout
        pyFiles = '\n'.join(pyFilesList)
        print(f'''FEHLER: Datei {p} nicht in Abgabe enthalten.

Folgende Dateien mit der Endung .py wurden gefunden:

{pyFiles}''')
        sys.exit (FILE_NOT_FOUND_EXIT_CODE)
    fixEncoding(studentFile)
    print()
    print(f'## Überprüfe dass {p} beim Laden keinen Fehler verursacht ...')
    runRes = runWypp(studentFile, '--check-runnable')
    if runRes:
        print(f'## OK: {p} erfolgreich geladen')
    else:
        abort(f'''Datei {p} konnte nicht geladen werden.
Weiter oben finden Sie die Fehlermeldungen.''')
    print()
    print(f'## Führe Tests in {p} aus ...')
    testRes = runWypp(studentFile, '--check')
    if testRes:
        print(f'## OK: keine Testfehler in {p}')
    else:
        abort(f'''Datei {p} enthält fehlerhafte Tests
Falls Sie einen Test nicht zum Laufen bringen, müssen
Sie diesen Test auskommentieren.''')

def usage():
    print('## TECHNISCHER FEHLER: Kommandozeilenargument sind ungültig.')
    sys.exit(1)

def help():
    print(f'python3 {sys.argv[0]} EXERCISE_NO')
    sys.exit(1)

if __name__ == '__main__':
    args = sys.argv
    if len(args) != 2:
        usage()
    if "--help" in sys.argv:
        usage()
    opts = Options(exerciseNo=sys.argv[1])
    main(opts)
