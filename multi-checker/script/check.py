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
    py.add_argument('--assignment', metavar='X', type=str, help='Identifier for assignment')
    hs = subparsers.add_parser('haskell', help='Check haskell assignment')
    hs.add_argument('--sheet', metavar='X', type=str, help='Identifier for sheet')
    return parser.parse_args()

def getSheetFromEnv():
    title = os.environ.get('TASK_TITLE')
    i = title.rindex(' ')
    return title[i+1:].zfill(2)

if __name__ == '__main__':
    args = parseArgs()
    if args.debug:
        enableDebug()
    testDir = args.test_dir
    submissionDir = args.submission_dir or '.'
    submissionDir = submissionDir.rstrip('/')
    cmd = args.cmd
    if not cmd:
        bug('command not given on commandline')
    if cmd == 'python-wypp':
        wypp = args.wypp
        if not wypp:
            wypp = '/wypp'
        assignment = args.assignment
        if not assignment:
            bug('assignment not given on commandline')
        opts = python.PythonOptions(submissionDir, testDir, assignment, wypp)
        debug(f'Running python checks, options: {opts}')
        python.check(opts)
    elif cmd == 'haskell':
        debug('Running haskell checks')
        sheet = args.sheet
        if not sheet:
            sheet = getSheetFromEnv()
        opts = haskell.HaskellOptions(submissionDir, testDir, sheet)
        haskell.check(opts)
    else:
        bug(f'invalid kind: {cmd}')
