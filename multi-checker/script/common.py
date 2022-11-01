from dataclasses import dataclass
from typing import *

OK_WITH_WARNINGS_EXIT_CODE = 121

@dataclass
class Options:
    sourceDir: str
    testDir: Optional[str]

