from wypp import *

class Counter:
    def __init__(self, start):
        self.count = start

def add(x, *args, **kwargs):
    return x + len(args) + len(kwargs)

c = Counter(1)
check(c.count, 1)
check(add(1, 2, z=3), 3)
