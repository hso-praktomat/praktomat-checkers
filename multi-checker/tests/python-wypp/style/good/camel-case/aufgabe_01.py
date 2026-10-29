from __future__ import annotations
from wypp import *
from enum import Enum
from typing import Literal, TypeVar, Callable
import math

# Good examples from the style guide

days = 7
seconds = 31
running = True

@record
class Date:
    year: int
    month: int
    day: int

    def doNothing(self, param: int) -> None:
        pass

def someFunction(x: int) -> int:
    return x + 1

def doSomething() -> None:
    pass

condition = True
if condition:
    doSomething()
    # Good indentation

doSomething()

class Spam:
    def spam(self, h: int, d: dict[str, int], l: list[int]) -> str:
        return f'{h} {d} {l}'

x = Spam()
ham = [1, 2]
eggs = 'eggs'
lst = [1, 2, 3, 4]
name = x.spam(ham[1], {eggs: -2}, lst[1:2:3])

def calculateSomething(param: int) -> float:
    # body
    return param * 2.5

# More camelCase code following the style guide

MAX_SPEED = 120
__all__ = ['Date', 'someFunction']

Color = Literal['red', 'green', 'blue']
Number = int | float
T = TypeVar('T')

class Weekday(Enum):
    MONDAY = 1
    TUESDAY = 2

@record
class Point:
    x: float
    y: float

class Counter:
    INITIAL = 0

    def __init__(self, start: int) -> None:
        self.count = start
        self.lastValue = start
        self._secret = 0
        self.__veryPrivate = 1

    def increment(self, by: int = 1) -> None:
        self.count += by

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Counter) and other.count == self.count

    def __repr__(self) -> str:
        return f'Counter({self.count:3d}, {self.lastValue!r})'

    @staticmethod
    def fromList(values: list[int]) -> Counter:
        return Counter(sum(values))

def _helper(x: int, *args: int, **kwargs: str) -> int:
    return x + len(args) + len(kwargs)

def applyTwice(f: Callable[[int], int], x: int) -> int:
    def inner(y: int) -> int:
        return f(f(y))
    return inner(x)

def distance(p: Point, q: Point) -> float:
    dx = p.x - q.x
    dy = p.y - q.y
    return math.sqrt(dx ** 2 + dy ** 2)

def sliceExamples(lst: list[int], i: int) -> list[int]:
    return lst[1:2] + lst[i + 1:] + lst[:-1] + lst[::2]

def whitespaceExamples(a: int, b: int) -> int:
    x = -2
    y = x * -1
    flag = not (x < y) and a <= b or x != -1
    pair = (1,)
    squares = [n * n for n in range(10) if n % 2 == 0]
    adder = lambda u, v: u + v
    point = Point(x=1.0, y=-2.0)
    return adder(x, y) + len(squares) + len(pair) + int(flag) + int(point.x)

def loopExamples(words: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for i, word in enumerate(words):
        counts[word] = counts.get(word, 0) + i
    for _ in range(3):
        pass
    try:
        value = int(words[0])
    except ValueError as err:
        print(err)
        value = 0
    counts['value'] = value
    return counts

def colorName(c: Color) -> str:
    match c:
        case 'red':
            return 'Rot'
        case _:
            return 'Andere'

# This line is exactly 120 characters long. xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

check(someFunction(1), 2)
check(calculateSomething(2), 5.0)
check(applyTwice(someFunction, 1), 3)
check(sliceExamples([1, 2, 3, 4, 5], 1), [2, 3, 4, 5, 1, 2, 3, 4, 1, 3, 5])
check(Counter.fromList([1, 2]), Counter(3))
check(colorName('red'), 'Rot')
check(distance(Point(0, 0), Point(3, 4)), 5.0)
check(loopExamples(['1', 'a']), {'1': 0, 'a': 1, 'value': 1})
check(whitespaceExamples(1, 2), 8)
