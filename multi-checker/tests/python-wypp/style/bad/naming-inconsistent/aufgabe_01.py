from wypp import *

def firstFunction(someValue: int) -> int:
    otherValue = someValue + 1
    return otherValue

def second_function(x: int) -> int:
    return x

def thirdFunction(y: int) -> int:
    return y

check(firstFunction(1), 2)
check(second_function(1), 1)
check(thirdFunction(1), 1)
