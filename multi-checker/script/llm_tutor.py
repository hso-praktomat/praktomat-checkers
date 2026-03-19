from dataclasses import dataclass
from typing import Optional
import os, sys, shlex

import yaml  # pip install pyyaml

from utils import *
from common import Options, runWithTimeout, testTimeoutSeconds
from exercise import parseExercise


THIS_DIR = os.path.dirname(os.path.abspath(__file__))  # ...\multi-checker\script

# 4 Ebenen hoch: Bachelor_Wehr
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", "..", "..", ".."))

TUTOR_ROOT = os.path.join(PROJECT_ROOT, "Tutor_chatbot")

DEFAULT_TUTOR_PY = os.path.join(TUTOR_ROOT, ".venv", "Scripts", "python.exe")
DEFAULT_TUTOR_MAIN = os.path.join(TUTOR_ROOT, "src", "praktomat_entry.py")

default_cmd = f'"{DEFAULT_TUTOR_PY}" "{DEFAULT_TUTOR_MAIN}"'

@dataclass
class LlmTutorOptions(Options):
    fakeLlm: bool
    sheet: Optional[str] = None
   

def check(opts: LlmTutorOptions):

    # 1) test-dir (llm-tutor) und exercise.yaml finden
    if opts.testDir is None:
        abort("testDir fehlt (erwarte --test-dir TEST_DIR)")

    test_dir = abspath(opts.testDir)
    exercise_path = pjoin(test_dir, "exercise.yaml")

    if not isFile(exercise_path):
        abort(f"exercise.yaml nicht gefunden: {exercise_path}")

    # 2) YAML roh laden, um meta auszulesen
    raw = yaml.safe_load(readFile(exercise_path))
    if not isinstance(raw, dict):
        abort("exercise.yaml hat kein gültiges YAML-Top-Level-Dict")

    meta = raw.get("meta", {})
    if meta is None:
        meta = {}
    if not isinstance(meta, dict):
        abort("meta muss ein YAML-Dict sein (z.B. meta: {task_pdf: ..., model_solution: ...})")

    pdf_rel = meta.get("task_pdf")
    ms_rel = meta.get("model_solution")

    if not pdf_rel or not ms_rel:
        abort("meta.task_pdf und meta.model_solution müssen gesetzt sein")

    task_pdf = pjoin(test_dir, pdf_rel)
    model_solution = pjoin(test_dir, ms_rel)

    if not isFile(task_pdf):
        abort(f"Aufgaben-PDF nicht gefunden: {task_pdf}")
    if not (isFile(model_solution) or isDir(model_solution)):
        abort(f"Musterlösung nicht gefunden: {model_solution}")

    # 3) Assignments parsen (liefert z.B. Aufgabe 3 + src: pizza.py)
    ex = parseExercise(opts.sheet or "default", exercise_path)

    if not ex.assignments:
        abort("Keine Assignments in exercise.yaml gefunden (Keys müssen z.B. '3:' sein)")

    # 4) Abgabe-Root finden
    submission_root = findSolutionDir(abspath(opts.sourceDir))

    # Lokaler Default (dein PC)
    cmd_str = os.getenv("LLM_TUTOR_CMD", default_cmd)

    any_called = False
    for a in ex.assignments:
        if not a.src:
            continue

        assignment_id = a.id  # "3"
        student_path = findFile(a.src, submission_root, ignoreCase=True)
        if not student_path:
            abort(f"Student-Datei für Aufgabe {assignment_id} nicht gefunden: {a.src}")

        cmd = shlex.split(cmd_str) + [
            "--pdf", task_pdf,
            "--model-solution", model_solution,
            "--student-solution", student_path,
            "--assignment", assignment_id,
        ]

        # for testing cases
        if opts.fakeLlm:
            print("Dummy Result: \n")
            print(cmd , "\n")
            return 
    
        res = runWithTimeout(cmd, timeout=testTimeoutSeconds(180), what="running LLM tutor")

        if res.exitcode != 0:
            sys.exit(1)

        any_called = True

    if not any_called:
        abort("Kein Assignment mit src gefunden (src fehlt in exercise.yaml?)")

    sys.exit(0)



# python check.py --submission-dir ..\tests\llm-tutor\loesung --test-dir ..\tests\llm-tutor llm-tutor --fake-llm True