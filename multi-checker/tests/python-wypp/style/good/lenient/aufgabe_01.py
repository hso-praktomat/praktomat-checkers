from wypp import *
from enum import Enum
import unittest

# Code the style check deliberately accepts, because in doubt it should be lenient.

# Short names and German names cannot be checked automatically (rules 1 and 2).
a = 7
anzahlTage = 7

# German names with umlauts
class Übung:
    def __init__(self, größe: int) -> None:
        self.größe = größe

def berechneFläche(länge: int, breite: int) -> int:
    return länge * breite

# UPPER_CASE for constants, also local ones, and arbitrary names for enum members
MAX_SPEED = 120

class Farbe(Enum):
    Rot = 1
    GRUEN = 2

class Konto:
    # __init__ needs no return type annotation, with or without parameters
    def __init__(self):
        self.stand = 0

class Person:
    def __init__(self, name: str, alter: int):
        self.name = name
        self.alter = alter

def summe(xs: list[int], i: int) -> int:
    N = len(xs)
    # no spaces around arithmetic operators
    return xs[i+1] + N*2 + 1

def ausgabe(x: int, y: int=0) -> None:
    # spaces around = for keyword arguments and no spaces for annotated defaults
    print(x, y, end = '')

def ausgerichtet() -> int:
    # several spaces to align assignments
    kurz      = 1
    langerName = 2
    return kurz + langerName

def ifOhneLeerzeichen(x: int) -> bool:
    if(x > 0):
        return True
    #Kommentar ohne Leerzeichen
      # Kommentar mit falscher Einrueckung
    return False

# A line consisting only of a long URL may exceed 120 characters:
# https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range-and-some-more-characters-to-be-long

# Test methods may use the test_ prefix of unittest, although this file uses camelCase
class TestSumme(unittest.TestCase):
    def test_summe(self) -> None:
        self.assertEqual(summe([1, 2, 3], 0), 2 + 3*2 + 1)

    def test_summe_ende(self) -> None:
        self.assertEqual(summe([1, 2, 3], 1), 3 + 3*2 + 1)

check(summe([1, 2, 3], 0), 9)
check(ausgerichtet(), 3)
check(ifOhneLeerzeichen(1), True)
check(Person('Anna', 20).alter, 20)
check(Konto().stand, 0)
check(berechneFläche(2, 3), 6)
check(Übung(3).größe, 3)
