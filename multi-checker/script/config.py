from __future__ import annotations
from dataclasses import dataclass
from typing import Union
from utils import *
import yaml



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
class LlmTutorConfig:
    apikey: str

    @staticmethod
    def parse(v: YamlDict):
        apikey = v.get("apikey")
        return LlmTutorConfig(apikey)


@dataclass
class Config:
    llmTutorConfig: LlmTutorConfig

    @staticmethod
    def parse(v: YamlDict):
        llm_tutor_raw = v.get("llmTutorConfig", {})
        llm_tutor_cfg = LlmTutorConfig.parse(YamlDict(llm_tutor_raw))
        return Config(llmTutorConfig=llm_tutor_cfg)
    

def parseConfig(yamlPath: str) -> Config:
    s = readFile(yamlPath)
    ymlDict = yaml.safe_load(s)
    cfg = Config.parse(YamlDict(ymlDict))
    print(f"Parsed config from {yamlPath}: {cfg}")
    return cfg