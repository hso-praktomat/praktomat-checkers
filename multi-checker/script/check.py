from utils import *
from common import *
import python
import haskell
import argparse

def parseArgs():
    parser = argparse.ArgumentParser(description='Checker for haskell assignments')
    parser.add_argument('--submission-dir', metavar='DIR', type=str,
                        help='Directories with student submission')
    parser.add_argument('--test-dir', metavar='DIR', type=str,
                        help='Directories with tests')
    subparsers = parser.add_subparsers(help='Commands', dest='cmd')
    parser.add_argument('--debug', help='Enable debug output',
                         action='store_true', default=False)
    py = subparsers.add_parser('python-wypp', help='Check python assignment')
    py.add_argument('--wypp', metavar='DIR', type=str, help='Path to wypp')
    py.add_argument('--sheet', metavar='X', type=str, help='Identifier for sheet')
    py.add_argument('--assignment', metavar='X', type=str, help='Identifier for assignment')
    hs = subparsers.add_parser('haskell', help='Check haskell assignment')
    hs.add_argument('--sheet', metavar='X', type=str, help='Identifier for sheet')
    return parser.parse_args()

def getSheetFromEnv():
    title = os.environ.get('TASK_TITLE')
    i = title.rindex(' ')
    return title[i+1:].zfill(2)

DEFAULT_TEST_DIR = '/external/praktomat-tests/haskell-advanced-prog'

if __name__ == '__main__':
    args = parseArgs()
    if args.debug:
        enableDebug()
    testDir = args.test_dir or DEFAULT_TEST_DIR
    testDir = abspath(testDir)
    submissionDir = args.submission_dir or '.'
    submissionDir = submissionDir.rstrip('/')
    submissionDir = abspath(submissionDir)
    cmd = args.cmd
    if not cmd:
        bug('command not given on commandline')
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
    if cmd == 'python-wypp':
        wypp = args.wypp
        if not wypp:
            wypp = '/wypp'
        sheet = args.sheet
        if not sheet:
            sheet = getSheetFromEnv()
        assignment = args.assignment
        opts = python.PythonOptions(submissionDir, testDir, sheet, assignment, wypp)
        debug(f'Running python checks, options: {opts}')
        python.check(opts)
    elif cmd == 'haskell':
        sheet = args.sheet
        if not sheet:
            sheet = getSheetFromEnv()
        opts = haskell.HaskellOptions(submissionDir, testDir, sheet)
        debug(f'Running haskell checks, options: {opts}')
        haskell.check(opts)
    else:
        bug(f'invalid kind: {cmd}')

