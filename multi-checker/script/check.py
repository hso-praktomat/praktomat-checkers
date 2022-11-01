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
    parser.add_argument('--kind', metavar='K', type=str,
                        help='Assignment kind (python-wypp or haskell)')
    parser.add_argument('--wypp', metavar='DIR', type=str,
                        help='Path to wypp')
    parser.add_argument('--debug', help='Enable debug output')
    parser.add_argument('exercise', metavar='X', type=str, help='Identifier for exercise')
    return parser.parse_args()

if __name__ == '__main__':
    args = parseArgs()
    testDir = args.test_dir
    submissionDir = args.submission_dir or '.'
    submissionDir = submissionDir.rstrip('/')
    exercise = args.exercise
    kind = args.kind
    wypp = args.wypp
    if not exercise:
        bug('exercise not given on commandline')
    if not kind:
        bug('kind not given on commandline')
    if not wypp:
        wypp = '/wypp'
    opts = Options(exercise, submissionDir, testDir, wypp)
    debug(f'Options: {opts}')
    if kind == 'python-wypp':
        debug('Running python checks')
        python.check(opts)
    elif kind == 'haskell':
        debug('Running haskell checks')
        haskell.check(opts)
    else:
        bug(f'invalid kind: {kind}')

