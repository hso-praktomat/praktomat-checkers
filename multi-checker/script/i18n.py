# Language of the messages of the checker (English or German) and their translation.
#
# The language is selected as in WYPP (wypp/lang.py and wypp/i18n.py), so that the checker and
# WYPP agree on the language:
# 1. The commandline option --lang en|de (see setLang).
# 2. Otherwise the locale of the system, checked again for every message (see pickLanguage).
# 3. Otherwise English.
#
# Messages are translated with tr, the English message is the key for the German translation
# in DE. multi-checker/tests/i18nTests.py checks that all messages passed to tr and trKey are
# translated.
from typing import Literal, MutableMapping, Optional
import locale
import os

Lang = Literal['en', 'de']
allLanguages: list[Lang] = ['en', 'de']
defaultLang: Lang = 'en'

_lang: Optional[Lang] = None

def parseLang(s: str) -> Optional[Lang]:
    for l in allLanguages:
        if l == s:
            return l
    return None

def setLang(lang: Lang) -> None:
    global _lang
    _lang = lang

def getLang() -> Lang:
    if _lang is not None:
        return _lang
    return pickLanguage(allLanguages, defaultLang)

def _langFromEnv(env: MutableMapping[str, str]) -> Optional[str]:
    # 1) GNU LANGUAGE: colon-separated fallbacks (e.g., "de:en_US:en")
    lng = env.get('LANGUAGE')
    if lng:
        for part in lng.split(':'):
            part = part.strip()
            if part:
                return part
    # 2) POSIX locale vars in order of precedence
    for var in ('LC_ALL', 'LC_MESSAGES', 'LANG'):
        val = env.get(var)
        if val and val not in ('C', 'POSIX'):
            return val
    # 3) locale module fallback
    try:
        locale.setlocale(locale.LC_CTYPE, '')
    except locale.Error:
        pass
    return locale.getlocale()[0]

def _normLang(tag: str) -> str:
    # "de-DE.UTF-8" -> "de_DE"
    tag = tag.replace('-', '_')
    if '.' in tag:
        tag = tag.split('.', 1)[0]
    return tag

def pickLanguage(supported: list[Lang], default: Lang) -> Lang:
    """
    Returns the supported language matching the locale of the system, as pickLanguage of WYPP.
    In practice, only LC_ALL, LC_CTYPE and LANG matter, because Python sets LC_CTYPE from
    the environment at startup, so getlocale() almost never returns None.
    """
    raw = locale.getlocale()[0]
    if not raw:
        raw = _langFromEnv(os.environ)
        if not raw:
            return default
    want = _normLang(raw)
    # exact match first
    for s in supported:
        if _normLang(s).lower() == want.lower():
            return s
    # fallback to language-only match (de_DE -> de)
    wantBase = want.split('_')[0].lower()
    for s in supported:
        if _normLang(s).split('_')[0].lower() == wantBase:
            return s
    return default

def tr(key: str, /, **args: object) -> str:
    """
    Translates the English message key into the current language and replaces the placeholders
    {name} in the message by the values of args. If args are given, literal braces in the message
    must be doubled.
    """
    msg = key
    if getLang() == 'de':
        msg = DE.get(key, key)
    if args:
        return msg.format(**args)
    return msg

def trKey(msg: str) -> str:
    """
    Marks msg as a message that is translated later by tr(msg).
    """
    return msg

DE: dict[str, str] = {
    # check.py, common.py, utils.py, exercise.py
    'Invalid language {lang}, must be en or de': 'Ungültige Sprache {lang}, erlaubt sind en und de',
    'command not given on commandline': 'Kein Kommando auf der Kommandozeile angegeben',
    'Timeout after {timeout}s while {what}': 'Zeitüberschreitung nach {timeout}s {what}',
    'ERROR: {msg}': 'FEHLER: {msg}',
    'Fixed encoding of {file}': 'Kodierung von {file} korrigiert',
    'Config option "{key}" must be a boolean': 'Konfigurationsoption "{key}" muss ein Wahrheitswert sein',
    'Config option "{key}" must be an int': 'Konfigurationsoption "{key}" muss eine ganze Zahl sein',
    'Config option "{key}" must be a string: {value}': 'Konfigurationsoption "{key}" muss ein String sein: {value}',
    'Assignment {id} not defined in exercise file': 'Aufgabe {id} ist in der Datei exercise.yaml nicht definiert',
    'Config error: {msg}': 'Konfigurationsfehler: {msg}',
    # testContext.py
    'FAIL': 'FEHLER',
    'OK_BUT_SOME_MISSING': 'OK, ABER DATEIEN FEHLEN',
    'Dumped test results to {file}': 'Testergebnisse gespeichert in {file}',
    'ERROR': 'FEHLER',
    '{title} status: {status}': 'Status {title}: {status}',
    'No tests found': 'Keine Tests gefunden',
    'Test results:': 'Testergebnisse:',
    'points': 'Punkte',
    '({total} tests, {errors} errors, {failures} failures)': '({total} Tests, {errors} Fehler, {failures} Fehlschläge)',
    'no tests': 'keine Tests',
    'Assignment {id}:': 'Aufgabe {id}:',
    'Total points: {points}/{max} (preliminary, subject to change!)':
        'Gesamtpunkte: {points}/{max} (vorläufig, Änderungen vorbehalten!)',
    '{title} output': 'Ausgabe: {title}',
    'Output of coding conventions check': 'Ausgabe der Prüfung der Programmierkonventionen',
    'Output for test of assignment {id} ({file})': 'Ausgabe des Tests für Aufgabe {id} ({file})',
    'Test for assignment {id} is required to succeed but failed!':
        'Der Test für Aufgabe {id} muss erfolgreich sein, ist aber fehlgeschlagen!',
    'Aborting': 'Abbruch',
    'Script {file} does not exist': 'Das Skript {file} existiert nicht',
    # python.py
    'running {file} via WYPP, testFile={testFile}': 'beim Ausführen von {file} mit WYPP, Testdatei={testFile}',
    'Test file {file} does not exist': 'Die Testdatei {file} existiert nicht',
    'running unittests in {file}': 'beim Ausführen der Unittests in {file}',
    'ERROR: File {file} not part of the submission. I found the following files:\n\n{files}':
        'FEHLER: Die Datei {file} ist nicht Teil der Abgabe. Folgende Dateien habe ich gefunden:\n\n{files}',
    'Only checking that file {file} exists, not loading.':
        'Es wird nur geprüft, ob die Datei {file} existiert, sie wird nicht geladen.',
    '## Checking that {file} loads successfully ...': '## Prüfe, ob {file} erfolgreich geladen werden kann ...',
    '## OK: {file} loads successfully': '## OK: {file} kann erfolgreich geladen werden',
    'File {file} could not be loaded.\nYou find more error messages above.':
        'Die Datei {file} konnte nicht geladen werden.\nWeitere Fehlermeldungen findest du weiter oben.',
    '## Executing tests in {file} ...': '## Führe die Tests in {file} aus ...',
    '## OK: no test failures in {file}': '## OK: keine fehlgeschlagenen Tests in {file}',
    'Timeout for tests in {file}. Probably there is an infinite loop!':
        'Zeitüberschreitung bei den Tests in {file}. Wahrscheinlich gibt es eine Endlosschleife!',
    'File {file} contains test failures!\nIf you cannot make a test succeed, you have to comment it out.':
        'Die Datei {file} enthält fehlgeschlagene Tests!\n'
        'Wenn du einen Test nicht zum Laufen bringst, musst du ihn auskommentieren.',
    'Checking assignment {id} (file: {file})': 'Prüfe Aufgabe {id} (Datei: {file})',
    'Summary': 'Zusammenfassung',
    '{file}: not found': '{file}: nicht gefunden',
    '{file}: failed': '{file}: fehlgeschlagen',
    'Coding conventions: {status}': 'Programmierkonventionen: {status}',
    'Error: at least one assignment failed!': 'Fehler: mindestens eine Aufgabe ist fehlgeschlagen!',
    'Warn: at least one assignment not found': 'Warnung: mindestens eine Aufgabe wurde nicht gefunden',
    'Configuration error: src option not set for assignment {id}':
        'Konfigurationsfehler: Die Option src ist für Aufgabe {id} nicht gesetzt',
    'Load and student tests': 'Laden und eigene Tests',
    '## Checking coding conventions of {file} ...': '## Prüfe die Programmierkonventionen in {file} ...',
    '## OK: {file} follows the coding conventions': '## OK: {file} hält die Programmierkonventionen ein',
    'File {file} violates the coding conventions.': 'Die Datei {file} verletzt die Programmierkonventionen.',
    'All files missing': 'Alle Dateien fehlen',
    'Option --assignment not given, exercise file {file} not found':
        'Die Option --assignment fehlt und die Datei {file} wurde nicht gefunden',
    # pythonStyle.py: the coding conventions
    '- Names of functions, methods, parameters, variables and attributes start with a lowercase letter\n'
    '  and use camelCase. snake_case is also allowed, but use only one of the two styles in a file.':
        '- Namen von Funktionen, Methoden, Parametern, Variablen und Attributen beginnen mit einem Kleinbuchstaben\n'
        '  und verwenden camelCase. snake_case ist auch erlaubt, aber verwende in einer Datei nur einen der beiden '
        'Stile.',
    '- Names of classes, records and types (Literal, Union) start with an uppercase letter and use\n  CamelCase.':
        '- Namen von Klassen, Records und Typen (Literal, Union) beginnen mit einem Großbuchstaben und\n'
        '  verwenden CamelCase.',
    '- Lines have at most 120 characters.': '- Zeilen haben höchstens 120 Zeichen.',
    '- Indent code with 4 spaces, do NOT use tabs. This might require to change the settings of your editor.':
        '- Rücke Code mit 4 Leerzeichen ein, verwende KEINE Tabulatoren. Eventuell musst du dafür die '
        'Einstellungen deines Editors ändern.',
    '- No space between the name of a function and the opening parenthesis: doSomething()':
        '- Kein Leerzeichen zwischen dem Namen einer Funktion und der öffnenden Klammer: doSomething()',
    '- No space directly after an opening or before a closing bracket: spam(ham[1], {eggs: 2})':
        '- Kein Leerzeichen direkt nach einer öffnenden oder vor einer schließenden Klammer: spam(ham[1], {eggs: 2})',
    '- No space before but one space after a comma or a colon: f(a, b), {eggs: 2}, x: int':
        '- Kein Leerzeichen vor, aber ein Leerzeichen nach einem Komma oder Doppelpunkt: f(a, b), {eggs: 2}, x: int',
    '- One space on both sides of =, ==, +=, <, <=, -> and other operators: x = y, def f() -> int':
        '- Ein Leerzeichen auf beiden Seiten von =, ==, +=, <, <=, -> und anderen Operatoren: x = y, def f() -> int',
    '- All parameters (except self) and the results of functions and methods have type annotations:\n'
    '  def calculateSomething(param: int) -> float':
        '- Alle Parameter (außer self) und die Ergebnisse von Funktionen und Methoden haben Typannotationen:\n'
        '  def calculateSomething(param: int) -> float',
    # pythonStyle.py: messages of ruff
    'Line too long ({width} > {limit})': 'Zeile zu lang ({width} > {limit} Zeichen)',
    'Indentation is not a multiple of {indentWidth}': 'Einrückung ist kein Vielfaches von {indentWidth}',
    'Over-indented': 'Zu weit eingerückt',
    'Over-indented (comment)': 'Zu weit eingerückt (Kommentar)',
    'Indentation contains tabs': 'Einrückung enthält Tabulatoren',
    "Whitespace before '{symbol}'": "Überflüssiges Leerzeichen vor '{symbol}'",
    "Whitespace after '{symbol}'": "Überflüssiges Leerzeichen nach '{symbol}'",
    'Missing whitespace around operator': 'Leerzeichen um Operator fehlt',
    'Missing whitespace after {symbol}': 'Leerzeichen nach {symbol} fehlt',
    'Missing type annotation for function argument `{name}`': 'Typannotation für Parameter `{name}` fehlt',
    'Missing type annotation for `*{name}`': 'Typannotation für `*{name}` fehlt',
    'Missing type annotation for `**{name}`': 'Typannotation für `**{name}` fehlt',
    'Missing return type annotation for public function `{name}`': 'Rückgabetyp der Funktion `{name}` fehlt',
    'Missing return type annotation for private function `{name}`':
        'Rückgabetyp der privaten Funktion `{name}` fehlt',
    'Missing return type annotation for special method `{name}`':
        'Rückgabetyp der speziellen Methode `{name}` fehlt',
    'Missing return type annotation for staticmethod `{name}`': 'Rückgabetyp der statischen Methode `{name}` fehlt',
    'Missing return type annotation for classmethod `{name}`': 'Rückgabetyp der Klassenmethode `{name}` fehlt',
    # pythonStyle.py: naming conventions
    'Function name "{name}"': 'Funktionsname "{name}"',
    'Method name "{name}"': 'Methodenname "{name}"',
    'Parameter name "{name}"': 'Parametername "{name}"',
    'Variable name "{name}"': 'Variablenname "{name}"',
    'Attribute name "{name}"': 'Attributname "{name}"',
    'Class name "{name}"': 'Klassenname "{name}"',
    'Type alias name "{name}"': 'Name des Typalias "{name}"',
    'Type variable name "{name}"': 'Name der Typvariable "{name}"',
    '{what} is in {style}, but most names in this file are in {mainStyle}':
        '{what} ist in {style}, aber die meisten Namen in dieser Datei sind in {mainStyle}',
    '{what} does not follow the naming conventions: use CamelCase, starting with an uppercase letter':
        '{what} entspricht nicht den Namenskonventionen: verwende CamelCase, beginnend mit einem Großbuchstaben',
    '{what} does not follow the naming conventions: use camelCase or snake_case, starting with a lowercase letter':
        '{what} entspricht nicht den Namenskonventionen: verwende camelCase oder snake_case, beginnend mit einem '
        'Kleinbuchstaben',
    # pythonStyle.py: output of the check of the coding conventions
    '{file}: coding conventions not checked because of syntax errors':
        '{file}: Programmierkonventionen wegen Syntaxfehlern nicht geprüft',
    'Checking coding conventions of {files}': 'Prüfe die Programmierkonventionen in {files}',
    'No violations of the coding conventions found.': 'Keine Verstöße gegen die Programmierkonventionen gefunden.',
    '... and {n} more violations in {file}': '... und {n} weitere Verstöße in {file}',
    'Found {n} violation(s) of the coding conventions.': '{n} Verstoß/Verstöße gegen die Programmierkonventionen gefunden.',
    'Please follow these coding conventions:': 'Bitte halte dich an diese Programmierkonventionen:',
    'File {file} does not exist': 'Die Datei {file} existiert nicht',
    'Coding conventions not checked, because all files contain syntax errors':
        'Programmierkonventionen nicht geprüft, weil alle Dateien Syntaxfehler enthalten',
    # java.py
    'No build file found: {files}': 'Keine Build-Datei gefunden: {files}',
    'running gradle task {task}': 'beim Ausführen des Gradle-Tasks {task}',
    'Checking coding conventions FAILED': 'Prüfung der Programmierkonventionen FEHLGESCHLAGEN',
    'Here are the coding conventions to follow:': 'Diese Programmierkonventionen musst du einhalten:',
    '- Naming conventions': '- Namenskonventionen',
    '  - All identifiers except for constants in camel case, do not use underscores to separate words':
        '  - Alle Bezeichner außer Konstanten in camelCase, keine Unterstriche zum Trennen von Wörtern',
    '  - Names of classes, interfaces, records and enums start with an uppercase letters':
        '  - Namen von Klassen, Interfaces, Records und Enums beginnen mit einem Großbuchstaben',
    '  - Names of methods and variables start with a lowercase letter':
        '  - Namen von Methoden und Variablen beginnen mit einem Kleinbuchstaben',
    '  - Names of constants are written in SCREAMING_CASE': '  - Namen von Konstanten werden in SCREAMING_CASE geschrieben',
    '- Indentation': '- Einrückung',
    '  - Indent a block with four spaces': '  - Rücke einen Block mit vier Leerzeichen ein',
    '  - Do NOT use tabs, this might require to change the settings of your IDE':
        '  - Verwende KEINE Tabulatoren, eventuell musst du dafür die Einstellungen deiner IDE ändern',
    'ERROR: The following files are missing in your submission:': 'FEHLER: Folgende Dateien fehlen in deiner Abgabe:',
    'The following .java files are present:': 'Folgende .java-Dateien sind vorhanden:',
    'No java files found in your submission': 'Keine Java-Dateien in deiner Abgabe gefunden',
    'All files missing, aborting': 'Alle Dateien fehlen, Abbruch',
    'Compile': 'Kompilieren',
    'Configuration error: test directory {dir} does not exist in {sheetDir}.':
        'Konfigurationsfehler: Das Testverzeichnis {dir} existiert nicht in {sheetDir}.',
    'Directory {dir} required for one of the selected assignments does not exist':
        'Das Verzeichnis {dir}, das für eine der ausgewählten Aufgaben benötigt wird, existiert nicht',
    # haskell.py
    '"{cmd}" failed\n\n{output}': '"{cmd}" ist fehlgeschlagen\n\n{output}',
    'Cannot parse test output!': 'Die Ausgabe der Tests kann nicht verarbeitet werden!',
    'Source file {file} contains illegal pragma: {pragma}': 'Die Quelldatei {file} enthält ein unerlaubtes Pragma: {pragma}',
    'ERROR: File {file} not included in submission. I found the following .hs files:':
        'FEHLER: Die Datei {file} ist nicht Teil der Abgabe. Folgende .hs-Dateien habe ich gefunden:',
    'All source files missing!': 'Alle Quelldateien fehlen!',
    # llm_tutor.py
    'Uploading the solution to an LLM was not permitted. Aborting.':
        'Das Hochladen der Lösung zu einem LLM ist nicht erlaubt. Abbruch.',
    'No test file defined for assignment {id}': 'Keine Testdatei für Aufgabe {id} definiert',
    'No extra file defined for assignment {id}': 'Keine Zusatzdatei für Aufgabe {id} definiert',
    'No source file defined for assignment {id}': 'Keine Quelldatei für Aufgabe {id} definiert',
}
