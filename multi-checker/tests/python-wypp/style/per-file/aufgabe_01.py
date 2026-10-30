from wypp import *

@record
class Time:
    hours: int
    minutes: int

def secondsSinceMidnight(t: Time) -> int:
    return t.hours * 3600 + t.minutes * 60

x=1
check(secondsSinceMidnight(Uhrzeit(1, 0)), 3600)
