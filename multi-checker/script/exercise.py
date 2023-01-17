# AST and parser for exercise.yaml files
from __future__ import annotations
from common import *
from utils import *
from shell import *
import yaml
import re
from typing import *

class YamlDict:
    def __init__(self, dicts: Union[dict, list[dict]]):
        if isinstance(dicts, list):
            self.__dicts = dicts
        else:
            self.__dicts = [dicts]
    def get(self, key, default=None):
        for d in self.__dicts:
            if key in d:
                return d[key]
        return default
    def items(self):
        return self.__dicts[0].items()
    def extend(self, d):
        if d is None:
            raise ValueError('d must not be None')
        return YamlDict([d] + self.__dicts)

@dataclass
class Assignment:
    sheet: str
    id: str
    points: int
    src: str         # the name of the source file
    tests: list[str] # test files, can be empty
    testOkRequired: bool
    testScript: Optional[str]
    def parse(sheet: str, v: YamlDict, id: int):
        src = v.get('src')
        tests = asList(v.get('test', [])) + asList(v.get('tests', []))
        points = v.get('points', -1)
        try:
            points = int(points)
        except ValueError:
            bug('error parsing exercise.yaml: points must be a number')
        testOkRequired = v.get('test-ok-required', False)
        testScript = v.get('test-script')
        return Assignment(sheet, id, points, src, tests, testOkRequired, testScript)

assignmentIdRe = re.compile(r'\d+[a-z]?')

@dataclass
class Exercise:
    sheet: str
    assignments: list[Assignment]
    def parse(sheet: str, ymlDict: YamlDict) -> Exercise:
        assignments = []
        for k, v in ymlDict.items():
            if type(k) == int:
                k = str(k)
            if type(k) != str or not assignmentIdRe.match(k):
                continue # not an assignment
            a = Assignment.parse(sheet, ymlDict.extend(v), k)
            assignments.append(a)
        return Exercise(sheet, assignments)

def parseExercise(sheet, yamlPath):
    s = readFile(yamlPath)
    ymlDict = yaml.load(s, Loader=yaml.FullLoader)
    return Exercise.parse(sheet, YamlDict(ymlDict))
