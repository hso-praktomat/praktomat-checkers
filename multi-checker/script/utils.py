import sys
from typing import *
from shell import *
import codecs

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
# Characters to replace
replacements = ['ä', 'ö', 'ü', 'Ä', 'Ö', 'Ü', 'ß']
# Byte order marks
boms = {codecs.BOM_UTF8: 'utf_8',
        codecs.BOM_UTF16_LE: 'utf_16_le',
        codecs.BOM_UTF16_BE: 'utf_16_be',
        codecs.BOM_UTF32_LE: 'utf_32_le',
        codecs.BOM_UTF32_BE: 'utf_32_be'}
def fixEncoding(path):
    bytes_orig = open(path, 'rb').read()
    bytes = bytes_orig
    for b, enc in boms.items():
        if b == bytes[:len(b)]:
            bytes = bytes[len(b):]
            bytes = bytes.decode(enc).encode('utf_8')
            break
    else:
        # no BOM
        for r in replacements:
            bytes = bytes.replace(r.encode('iso-8859-1'), r.encode('utf-8'))
    if bytes != bytes_orig:
        open(path, 'wb').write(bytes)
        print(f'Fixed encoding of {path}')

def fixEncodingRecursively(startDir: str, ext: str):
    files = run(f"find {startDir} -type f -name '*.{ext}'", captureStdout=splitLines).stdout
    for p in files:
        fixEncoding(p)

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

def removeLeading(full: str, leading: str):
    if full.startswith(leading):
        return full[len(leading)+1:]
    else:
        return full

_DEBUG = False

def enableDebug():
    global _DEBUG
    _DEBUG = True

def isDebug():
    return _DEBUG

def debug(msg):
    if _DEBUG:
        print(f'[DEBUG] {msg}')
