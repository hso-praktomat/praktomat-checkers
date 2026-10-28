# AST and parser for exercise.yaml files
from __future__ import annotations
from shell import *
from common import *
from utils import *
import yaml
import re
from typing import *

class YamlDict:
    def __init__(self, dicts: Union[dict[Any, Any], list[dict[Any, Any]]]) -> None:
        if isinstance(dicts, list):
            self.__dicts = dicts
        else:
            self.__dicts = [dicts]
    def get(self, key: str, default: Any=None) -> Any:
        for d in self.__dicts:
            if key in d:
                return d[key]
        return default
    def getBool(self, key: str, default: bool) -> bool:
        x = self.get(key)
        if x is None:
            return default
        if not isinstance(x, bool):
            abort(f'Config option "{key} must be a boolean')
        return x
    def getInt(self, key: str, default: int) -> int:
        x = self.get(key)
        if x is None:
            return default
        if not isinstance(x, int):
            abort(f'Config option "{key} must be an int')
        return x
    def getStr(self, key: str) -> Optional[str]:
        x = self.get(key)
        if x is None:
            return None
        if not isinstance(x, str):
            abort(f'Config option "{key} must be a string: {x}')
        return x
    def items(self) -> ItemsView[Any, Any]:
        return self.__dicts[0].items()
    def extend(self, d: Optional[dict[Any, Any]]) -> YamlDict:
        if d is None:
            raise ValueError('d must not be None')
        return YamlDict([d] + self.__dicts)

@dataclass
class PythonAssignmentConfig:
    wypp: bool         # check that the file loads and that type annotations are correct
    checkLoad: bool    # only check that the file loads (without type checking)
    @staticmethod
    def parse(v: YamlDict) -> PythonAssignmentConfig:
        wypp = v.getBool('python-wypp', True)
        load = v.getBool('python-load', True)
        return PythonAssignmentConfig(wypp, load)
    @property
    def typecheck(self) -> bool:
        return self.wypp and self.checkLoad

@dataclass
class Assignment:
    sheet: Optional[str]
    id: str
    points: int
    src: Optional[str]         # the name of the source file
    tests: list[str] # test files, can be empty
    testFilter: Optional[str]
    testOkRequired: bool
    testScript: Optional[str]
    pythonConfig: PythonAssignmentConfig
    extraFiles: list[str] # auxiliary files that can be used by the student code
    pdf: Optional[str] = None
    sampleSolution: Optional[str]  = None
    @staticmethod
    def parse(sheet: Optional[str], v: YamlDict, id: str) -> Assignment:
        src = v.getStr('src')
        tests = asList(v.get('test', [])) + asList(v.get('tests', []))
        testFilter = v.get('test-filter')
        extras = asList(v.get('extras', []))
        points = v.getInt('points', -1)
        pdf = v.getStr('pdf')
        sampleSolution = v.getStr('sampleSolution')
        try:
            points = int(points)
        except ValueError:
            bug('error parsing exercise.yaml: points must be a number')
        testOkRequired = v.getBool('test-ok-required', False)
        testScript = v.get('test-script')
        py = PythonAssignmentConfig.parse(v)
        return Assignment(sheet, id, points, src, tests, testFilter, testOkRequired, testScript, py, extras, pdf, sampleSolution)

assignmentIdRe = re.compile(r'\d+[a-z]?')

@dataclass
class Exercise:
    sheet: Optional[str]
    assignments: list[Assignment]
    @staticmethod
    def parse(sheet: Optional[str], ymlDict: YamlDict) -> Exercise:
        assignments: list[Assignment] = []
        for k, v in ymlDict.items():
            if type(k) == int:
                k = str(k)
            if type(k) != str or not assignmentIdRe.match(k):
                continue # not an assignment
            a = Assignment.parse(sheet, ymlDict.extend(v), k)
            assignments.append(a)
        return Exercise(sheet, assignments)
    def ensureAssignmentsDefined(self, assignmentIds: list[str]) -> None:
        allIds = [a.id for a in self.assignments]
        for x in assignmentIds:
            if x not in allIds:
                abort(f'Assignment {x} not defined in exercise file')

def parseExercise(sheet: Optional[str], yamlPath: str) -> Exercise:
    s = readFile(yamlPath)
    ymlDict = yaml.load(s, Loader=yaml.FullLoader)
    ex = Exercise.parse(sheet, YamlDict(ymlDict))
    debug(f"Parsed exercise from {yamlPath} for sheet {sheet}: {ex}")
    return ex

