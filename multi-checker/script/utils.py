import sys
from typing import *
from shell import *

def bug(msg: str):
    print('INTERNAL ERROR: ' + msg)
    sys.exit(1)

def abort(msg: str):
    print('FEHLER: ' + msg)
    sys.exit(1)

def readFile(name):
    with open(name, 'r', encoding='utf-8') as f:
        return f.read()

def asList(x):
    if type(x) == list:
        return x
    if type(x) == tuple:
        return list(x)
    else:
        return [x]

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

def findFile(p: str, sourceDir: str) -> Optional[str]:
    cand = pjoin(sourceDir, p)
    if isFile(cand):
        return cand
    for x in ls(sourceDir):
        if isDir(x):
            cand = pjoin(x, p)
            if isFile(cand):
                return cand
    return None

_DEBUG = False

def enableDebug():
    global _DEBUG
    _DEBUG = True

def debug(msg):
    if _DEBUG:
        print(f'[DEBUG] {msg}')
