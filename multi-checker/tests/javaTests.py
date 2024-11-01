from testUtils import *

javaTestDir = f'{praktomatTestsLocal}/java-aud'
checkstyle = '/opt/praktomat-addons/checkstyle.jar'
localTestDir = f'{thisDir}/java-aud'

def test_java01():
    expectOk(f'python3 {checkScript} {checkScriptArgs} java --checkstyle {checkstyle} --sheet 01-intro',
        external=f'{javaTestDir}/01-intro', submissionDir=f'{javaTestDir}/01-intro/solution')

def test_java02():
    # Solution wrapped in another directory with failing tests
    expectFail(f'python3 {checkScript} {checkScriptArgs} java --checkstyle {checkstyle} --sheet 01-intro',
           121, external=f'{javaTestDir}/01-intro', submissionDir=f'{localTestDir}/passed-with-warnings/wrapper/')

def test_java03():
    # Submission with BOM and iso encoding and with failing tests
    expectFail(f'python3 {checkScript} {checkScriptArgs} java --checkstyle {checkstyle} --sheet 01-intro',
           121, external=f'{javaTestDir}/01-intro', submissionDir=f'{localTestDir}/passed-with-warnings/AuD_Assignment_01/')

def test_java04():
    # Submission with checkstyle errors
    expectFail(f'python3 {checkScript} {checkScriptArgs} java --checkstyle {checkstyle} --sheet 01-intro',
           external=f'{javaTestDir}/01-intro', submissionDir=f'{localTestDir}/fail/AuD_Assignment_01/')
