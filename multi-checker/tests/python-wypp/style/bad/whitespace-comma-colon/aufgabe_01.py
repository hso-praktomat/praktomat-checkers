from wypp import *

def add(x:int, y: int) -> int:
    return x + y

d = {'a':1}
check(add(1,2), 3)
check(add(1 , 2), 3)
check(d['a'], 1)
