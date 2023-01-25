from dataclasses import dataclass
from typing import *
from shell import *

OK_WITH_WARNINGS_EXIT_CODE = 121

@dataclass
class Options:
    sourceDir: str
    testDir: Optional[str]

def getSheetDir(testDir, sheet):
    return pjoin(testDir, 'sheet-' + sheet)

def replaceAll(l: list[str], repl: str, s: str) -> str:
    for x in l:
        s = s.replace(x, repl)
    return s
