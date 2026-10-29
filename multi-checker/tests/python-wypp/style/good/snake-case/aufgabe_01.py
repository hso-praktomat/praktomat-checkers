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

    def do_nothing(self, param: int) -> None:
        pass

def some_function(x: int) -> int:
    return x + 1

def do_something() -> None:
    pass

condition = True
if condition:
    do_something()
    # Good indentation

do_something()

class Spam:
    def spam(self, h: int, d: dict[str, int], l: list[int]) -> str:
        return f'{h} {d} {l}'

x = Spam()
ham = [1, 2]
eggs = 'eggs'
lst = [1, 2, 3, 4]
name = x.spam(ham[1], {eggs: -2}, lst[1:2:3])

def calculate_something(param: int) -> float:
    # body
    return param * 2.5

# More snake_case code following the style guide

MAX_SPEED = 120
__all__ = ['Date', 'some_function']

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
        self.last_value = start
        self._secret = 0
        self.__very_private = 1

    def increment(self, by: int = 1) -> None:
        self.count += by

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Counter) and other.count == self.count

    def __repr__(self) -> str:
        return f'Counter({self.count:3d}, {self.last_value!r})'

    @staticmethod
    def from_list(values: list[int]) -> Counter:
        return Counter(sum(values))

def _helper(x: int, *args: int, **kwargs: str) -> int:
    return x + len(args) + len(kwargs)

def apply_twice(f: Callable[[int], int], x: int) -> int:
    def inner(y: int) -> int:
        return f(f(y))
    return inner(x)

def distance(p: Point, q: Point) -> float:
    dx = p.x - q.x
    dy = p.y - q.y
    return math.sqrt(dx ** 2 + dy ** 2)

def slice_examples(lst: list[int], i: int) -> list[int]:
    return lst[1:2] + lst[i + 1:] + lst[:-1] + lst[::2]

def whitespace_examples(a: int, b: int) -> int:
    x = -2
    y = x * -1
    flag = not (x < y) and a <= b or x != -1
    pair = (1,)
    squares = [n * n for n in range(10) if n % 2 == 0]
    adder = lambda u, v: u + v
    point = Point(x=1.0, y=-2.0)
    return adder(x, y) + len(squares) + len(pair) + int(flag) + int(point.x)

def loop_examples(words: list[str]) -> dict[str, int]:
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

def color_name(c: Color) -> str:
    match c:
        case 'red':
            return 'Rot'
        case _:
            return 'Andere'

# This line is exactly 120 characters long. xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

check(some_function(1), 2)
check(calculate_something(2), 5.0)
check(apply_twice(some_function, 1), 3)
check(slice_examples([1, 2, 3, 4, 5], 1), [2, 3, 4, 5, 1, 2, 3, 4, 1, 3, 5])
check(Counter.from_list([1, 2]), Counter(3))
check(color_name('red'), 'Rot')
check(distance(Point(0, 0), Point(3, 4)), 5.0)
check(loop_examples(['1', 'a']), {'1': 0, 'a': 1, 'value': 1})
check(whitespace_examples(1, 2), 8)
