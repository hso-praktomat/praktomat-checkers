from dataclasses import dataclass
from typing import *

FILE_NOT_FOUND_EXIT_CODE = 121

@dataclass
class Options:
    exercise: str
    sourceDir: str
    testDir: Optional[str]
    wypp: str

