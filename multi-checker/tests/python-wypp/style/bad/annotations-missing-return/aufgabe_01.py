from wypp import *

class Counter:
    def __init__(self, start: int) -> None:
        self.count = start

    def increment(self, by: int):
        self.count = self.count + by

    def __str__(self):
        return f'Counter({self.count})'

def printCounter(c: Counter):
    print(c)

c = Counter(1)
c.increment(1)
printCounter(c)
check(str(c), 'Counter(2)')
