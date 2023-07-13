from dataclasses import dataclass
from typing import *
from shell import *

OK_WITH_WARNINGS_EXIT_CODE = 121

# Exit code of the timeout command on timeout
TIMEOUT_EXIT_CODE = 124

@dataclass
class Options:
    sourceDir: str
    testDir: Optional[str]
    resultFile: Optional[str]

def getSheetDir(testDir, sheet):
    return pjoin(testDir, sheet)

def replaceAll(l: list[str], repl: str, s: str) -> str:
    for x in l:
        s = s.replace(x, repl)
    return s

def testTimeoutSeconds():
    fromEnv = os.getenv('PRAKTOMAT_CHECKER_TEST_TIMEOUT')
    if fromEnv:
        try:
            return int(fromEnv)
        except TypeError:
            pass
    return 60

def addTimeoutCmd(cmd: list[str], timeout: Optional[int]):
    if timeout:
        return ['timeout', str(timeout)] + cmd
    else:
        return cmd
