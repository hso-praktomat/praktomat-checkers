from utils import *
from common import *
import python
import haskell
import java
import argparse
import re

def parseArgs():
    parser = argparse.ArgumentParser(description='Checker for haskell assignments')
    parser.add_argument('--submission-dir', metavar='DIR', type=str,
                        help='Directories with student submission')
    parser.add_argument('--test-dir', metavar='DIR', type=str,
                        help='Directories with tests')
    subparsers = parser.add_subparsers(help='Commands', dest='cmd')
    parser.add_argument('--debug', help='Enable debug output',
                         action='store_true', default=False)
    py = subparsers.add_parser('python', help='Check python assignment')
    py.add_argument('--wypp', metavar='DIR', type=str, help='Path to wypp')
    py.add_argument('--sheet', metavar='X', type=str, help='Identifier for sheet')
    py.add_argument('--assignment', metavar='X', type=str, help='Identifier for assignment')
    hs = subparsers.add_parser('haskell', help='Check haskell assignment')
    hs.add_argument('--sheet', metavar='X', type=str, help='Identifier for sheet')
    java = subparsers.add_parser('java', help='Check Java assignment')
    java.add_argument('--sheet', metavar='X', type=str, help='Identifier for sheet')
    java.add_argument('--checkstyle', metavar='JAR', type=str,
                        help='Path to the CheckStyle JAR file',
                        default='/opt/praktomat-addons/checkstyle.jar')
    java.add_argument('--gradle-online', action='store_true', default=False,
                      help='Use gradle in online mode, default is offline')
    (known, _other) = parser.parse_known_args()
    return known

# "Labortest 2, Gruppe A" -> ["labortest_2", labortest_2_gruppe_a"]
def candsFromTitle(origTitle: str) -> list[str]:
    comps = []
    for x in origTitle.split(','):
        x = x.strip()
        x = replaceAll(["/", "\\", " ", "\t"], "_", x)
        x = x.lower()
        comps.append(x)
    cands = []
    for i in range(len(comps)):
        c = "_".join(comps[:i+1])
        cands.append(c)
    cands.reverse()
    return cands

_numRe = re.compile(r'\b\d+\b')
def getSheetFromEnv(testDir):
    origTitle = os.environ.get('TASK_TITLE').strip()
    cands = candsFromTitle(origTitle)
    m = _numRe.search(origTitle)
    if m:
        cands.append(m.group(0).zfill(2))
    for c in cands: # first search for the more specific
        d = getSheetDir(testDir, c)
        if isDir(d):
            return c
    return cands[-1]  # prefer the more generic


_DEFAULT_TEST_DIR = '/external/praktomat-tests'

def getDefaultTestDir(cmd):
    if cmd == 'python':
        return pjoin(_DEFAULT_TEST_DIR, 'python-prog1')
    elif cmd == 'java':
        return pjoin(_DEFAULT_TEST_DIR, 'java-aud')
    else:
        return pjoin(_DEFAULT_TEST_DIR, 'haskell-advanced-prog')

if __name__ == '__main__':
    args = parseArgs()
    if args.debug:
        enableDebug()
    cmd = args.cmd
    if not cmd:
        bug('command not given on commandline')
    testDir = args.test_dir or getDefaultTestDir(cmd)
    testDir = abspath(testDir)
    submissionDir = args.submission_dir or '.'
    submissionDir = submissionDir.rstrip('/')
    submissionDir = abspath(submissionDir)
    debug(f'Running checks with args={args}')
    if isDebug():
        print('Current user: ', end='')
        run('whoami')
        print('Ulimits:')
        run('ulimit -a')
        print('Environment:')
        run('env')
        print('Block size: ', end='')
        run('stat -fc %s .', onError='ignore')
    if cmd == 'python':
        wypp = args.wypp
        if not wypp:
            wypp = '/wypp'
        sheet = args.sheet
        if not sheet:
            sheet = getSheetFromEnv(testDir)
        assignment = args.assignment
        opts = python.PythonOptions(submissionDir, testDir, sheet, assignment, wypp)
        debug(f'Running python checks, options: {opts}')
        python.check(opts)
    elif cmd == 'haskell':
        sheet = args.sheet
        if not sheet:
            sheet = getSheetFromEnv(testDir)
        opts = haskell.HaskellOptions(submissionDir, testDir, sheet)
        debug(f'Running haskell checks, options: {opts}')
        haskell.check(opts)
    elif cmd == 'java':
        sheet = args.sheet
        if not sheet:
            sheet = getSheetFromEnv(testDir)
        offline = not args.gradle_online
        opts = java.JavaOptions(submissionDir, testDir, sheet, args.checkstyle, offline)
        debug(f'Running Java checks, options: {opts}')
        java.check(opts)
    else:
        bug(f'invalid kind: {cmd}')

