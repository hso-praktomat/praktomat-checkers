from wypp import *

def my_solution(n):
    sum = 0
    for i in range(1, n+1):
        sum = sum + i
    return sum

check(my_solution(0), 0)
check(my_solution(4), 1)
