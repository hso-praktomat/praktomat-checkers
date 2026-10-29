from wypp import *

def longLine() -> str:
    return 'This line is 121 characters long. xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

check(len(longLine()) > 0, True)
