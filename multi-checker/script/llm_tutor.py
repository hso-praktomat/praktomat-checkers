from dataclasses import dataclass
from typing import Optional
import os

from shell import *
from utils import *
from common import *
from config import *
from exercise import parseExercise


def configError(s) -> NoReturn:
    abort('Config error: ' + s)

@dataclass
class LlmTutorOptions(Options):
    llm_tutor_dir: str
    solution_dir: Optional[str]
    pdf_dir: Optional[str]
    fakeLlm: bool
    configApi: str
    sheet: Optional[str]
   
   
# alle strings sind als pfad hier weitergegeben
def runLlmTutor (llmTutorPfad: str, fake_llm: bool, id: str, sampleSolution: str, studentSolution: str, pdf_task:str , configApi:str):
    args = ['python3', llmTutorPfad + '/src/praktomat_entry.py']

    args = args + [
            "--pdf", pdf_task,
            "--model-solution", sampleSolution,
            "--student-solution", studentSolution,
            "--assignment", id,
            "--api", configApi
    ]

    if fake_llm:
            print("Dummy Result: \n")
            print(args , "\n")
            return 
    else:
        debug(f'llmTutorPfad = {llmTutorPfad}')
        debug(f'args = {args}')
        res = run(args, onError='ignore', stderrToStdout=True, captureStdout=True)
        print(res.stdout)

        if res.exitcode != 0:
            raise RuntimeError('LLM-tutor failed')
    
    

def check(opts: LlmTutorOptions):
    if os.getenv('ALLOW_LLM_UPLOAD') != '1':
        print('Uploading the solution to an LLM was not permitted. Aborting.')
        return

    # Direction with the exercise.yaml file
    exTest_dir = getSheetDir(opts.testDir, opts.sheet)
    exYaml = pjoin(exTest_dir, 'exercise.yaml')
    if isFile(exYaml):
        ex = parseExercise(opts.sheet, exYaml)
    else:
        ex = None

    if ex is not None:
        for assignment in ex.assignments:
             
            # pfad zu Musterlösung 
            if assignment.sampleSolution is None:
                configError(f'No test file defined for assignment {assignment.id}')
            # Default solution dir is /solution, but can be overridden by --solution-dir
            if opts.solution_dir:
                exSampleSolution_pfad = pjoin(opts.solution_dir, assignment.sampleSolution)
            else:
                exSampleSolution_pfad = pjoin(exTest_dir, 'solution', assignment.sampleSolution)


            if assignment.pdf is None:
                configError(f'No extra file defined for assignment {assignment.id}')
            # Default pdf dir is /pdf, but can be overridden by --pdf-dir
            if opts.pdf_dir:
                pdf = pjoin(opts.pdf_dir, assignment.pdf)
            else:
                pdf = pjoin(exTest_dir, 'pdf', assignment.pdf)

            # student Solution
            debug(f'opts.sourceDir = {opts.sourceDir}')
            nestedSourceDir = findSolutionDir(opts.sourceDir, lambda x: isDir(pjoin(x, 'src')))
            debug(f'nestedDir for {assignment.id} = {nestedSourceDir}')
            debug(f'Contents of dourceDir: {ls(opts.sourceDir)}')

            if assignment.src is None:
                configError(f'No source file defined for assignment {assignment.id}')
            student_pfad = pjoin(nestedSourceDir, assignment.src)
            debug(f'studentPfad = {student_pfad}')

            #api 
            api = parseConfig(pjoin(opts.configApi, 'config.yaml'))

            # Result von Sprachmodell
            runLlmTutor(llmTutorPfad=opts.llm_tutor_dir,
                            fake_llm= opts.fakeLlm, 
                            id= assignment.id,
                            sampleSolution= exSampleSolution_pfad, 
                            studentSolution= student_pfad,
                            pdf_task= pdf, 
                            configApi = api.llmTutorConfig.apikey)

