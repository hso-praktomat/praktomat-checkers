from wypp import *

def isSmall(x: int)->bool:
    return x<10

y=1
y+=1
check(isSmall(y), True)
check(y==2, True)
