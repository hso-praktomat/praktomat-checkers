from wypp import *

def DoSomething(Param: int) -> int:
    Result = Param + 1
    return Result

check(DoSomething(1), 2)
