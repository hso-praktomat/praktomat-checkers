# AST and parser for exercise.yaml files
from __future__ import annotations
from common import *
from utils import *
from shell import *
import yaml
import re

@dataclass
class Assignment:
    sheet: str
    id: str
    points: int
    src: str         # the name of the source file
    tests: list[str] # test files, can be empty
    testOkRequired: bool
    testScript: Optional[str]
    def parse(sheet: str, v: dict, id: int, defSrc: str):
        if v:
            src = v.get('src', defSrc)
            tests = asList(v.get('test', [])) + asList(v.get('tests', []))
            points = v.get('points', -1)
            try:
                points = int(points)
            except ValueError:
                bug('error parsing exercise.yaml: points must be a number')
            testOkRequired = v.get('test-ok-required', False)
            testScript = v.get('test-script')
        else:
            src = defSrc
            tests = []
            points = 0
            testOkRequired = False
            testScript = None
        return Assignment(sheet, id, points, src, tests, testOkRequired, testScript)

assignmentIdRe = re.compile(r'\d+[a-z]?')

@dataclass
class Exercise:
    sheet: str
    assignments: list[Assignment]
    def parse(sheet: str, ymlDict: dict) -> Exercise:
        defSrc = ymlDict.get('src')
        assignments = []
        for k, v in ymlDict.items():
            if type(k) == int:
                k = str(k)
            if type(k) != str or not assignmentIdRe.match(k):
                continue # not an assignment
            a = Assignment.parse(sheet, v, k, defSrc)
            assignments.append(a)
        return Exercise(sheet, assignments)

def parseExercise(sheet, yamlPath):
    s = readFile(yamlPath)
    ymlDict = yaml.load(s, Loader=yaml.FullLoader)
    return Exercise.parse(sheet, ymlDict)
