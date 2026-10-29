from wypp import *
from typing import Literal

color = Literal['red', 'green']

def isRed(c: color) -> bool:
    return c == 'red'

check(isRed('red'), True)
