from dataclasses import dataclass
from typing import *
from shell import *
from utils import *

OK_WITH_WARNINGS_EXIT_CODE = 121

# Exit code of the timeout command on timeout
TIMEOUT_EXIT_CODES = [124, -9, 137]

@dataclass
class Options:
    sourceDir: str
    testDir: Optional[str]
    resultFile: Optional[str]

def getSheetDir(testDir: Optional[str], sheet: str):
    if testDir is None:
        return '/external'
    return pjoin(testDir, sheet)

def replaceAll(l: list[str], repl: str, s: str) -> str:
    for x in l:
        s = s.replace(x, repl)
    return s

def testTimeoutSeconds(default: int=60):
    fromEnv = os.getenv('PRAKTOMAT_CHECKER_TEST_TIMEOUT')
    debug('Timeout from environment: ' + str(fromEnv))
    if fromEnv:
        try:
            return int(fromEnv)
        except TypeError:
            pass
    return default

def runWithTimeout(cmd: list[str], timeout: Optional[int], what: str, env: dict=None):
    if timeout:
        cmd = ['timeout', '--kill-after', '2', str(timeout)] + cmd
    debug(f'Command: {" ".join(cmd)}')
    res = run(cmd, onError='ignore', env=env, stderrToStdout=True, captureStdout=True)
    if timeout and res.exitcode in TIMEOUT_EXIT_CODES:
        msg = f'Timeout after {timeout}s while {what}'
        newStdout = res.stdout
        if newStdout:
            newStdout = newStdout + '\n\n' + msg
        else:
            newStdout = msg
        return RunResult(newStdout, res.stderr, TIMEOUT_EXIT_CODES[0])
    else:
        return res
