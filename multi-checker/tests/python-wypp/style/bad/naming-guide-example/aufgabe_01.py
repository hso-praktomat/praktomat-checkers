from wypp import *

# Bad naming example from the style guide

@record
class date:
    Year: int
    Month: int
    Day: int
    def do_Nothing(self, param: int) -> None:
        pass

def some_Function(x: int) -> int:
    return x + 1

check(some_Function(1), 2)
