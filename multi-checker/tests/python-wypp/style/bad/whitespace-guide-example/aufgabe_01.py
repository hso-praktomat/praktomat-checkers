from wypp import *

# Bad whitespace example from the style guide

class Spam:
    def spam(self, h: int, d: dict[str, int], l: list[int]) -> str:
        return f'{h} {d} {l}'

x = Spam()
ham = [1, 2]
eggs = 'eggs'
lst = [1, 2, 3, 4]
name=x . spam( ham[ 1 ], { eggs: - 2 },lst[1 : 2: 3] )

check(name, "2 {'eggs': -2} [2]")
