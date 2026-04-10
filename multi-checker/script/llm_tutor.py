from dataclasses import dataclass
from typing import Optional
import os, sys, shlex

import yaml  # pip install pyyaml

from utils import *
from common import *
from exercise import parseExercise


@dataclass
class LlmTutorOptions(Options):
    llm_tutor_dir: str
    solution_dir: str
    pdf_dir: str
    sheet: Optional[str] = None
    fakeLlm: bool
   
   
# alle strings sind als pfad hier weitergegeben
def runLlmTutor (llmTutorPfad: str, fake_llm: bool, id: str, sampleSolution: str, studentSolution: str, pdf_task:str ):
    args = ['python3', llmTutorPfad + '/src/praktomat_entry.py']

    args = args + [
            "--pdf", pdf_task,
            "--model-solution", sampleSolution,
            "--student-solution", studentSolution,
            "--assignment", id,
    ]

    if fake_llm:
            print("Dummy Result: \n")
            print(args , "\n")
            return 
    else:
         None
    
    

def check(opts: LlmTutorOptions):
    # test dir, pfad zum exercise.yaml (mount a dir tests/llm-tutor > externel)
    exTest_dir = getSheetDir(opts)
    exYaml = pjoin(exTest_dir, 'exercise.yaml')
    if isFile(exYaml):
        ex = parseExercise(opts.sheet, exYaml)
    else:
        ex = None

    if ex is not None:
        for assignemnt in ex.assignments:
             
            # pfad zu Musterlösung (mount a dir > tests/llm-tutor/sampleSolution > solution)
            exSampleSolution_pfad = pjoin(getSolutionDir(opts.solution_dir), assignemnt.tests)

            # student Solution
            nestedSourceDir = findSolutionDir(opts.sourceDir)
            student_pfad = pjoin (nestedSourceDir, assignemnt.src)

            # aufgabe pfad extrahieren
            pdf = pjoin(getPdfDir(opts.pdf_dir), assignemnt.extraFiles)

            # Result von Sprachmodell
            runLlmTutor(llmTutorPfad=opts.llm_tutor_dir,
                            fake_llm= opts.fakeLlm, 
                            id= assignemnt.id,
                            sampleSolution= exSampleSolution_pfad, 
                            studentSolution= student_pfad,
                            pdf_task= pdf)


# python check.py --submission-dir ..\tests\llm-tutor\loesung --test-dir ..\tests\llm-tutor llm-tutor --fake-llm True