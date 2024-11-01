from testUtils import *

haskellTestDir = f'{praktomatTestsLocal}/haskell-advanced-prog'

def test_haskell01():
    expectOk(f'python3 {checkScript} {checkScriptArgs} haskell --sheet 02',
            external=f'{haskellTestDir}/02', submissionDir=f'{haskellTestDir}/solutions/02')

def test_haskell02():
    expectFail(f'python3 {checkScript} {checkScriptArgs} haskell --sheet 02',
            1, external=f'{haskellTestDir}/02', submissionDir=f'{thisDir}/haskell/02-no-file')

def test_haskell03():
    expectFail(f'python3 {checkScript} {checkScriptArgs} haskell --sheet 05',
            121, external=f'{haskellTestDir}/05', submissionDir=f'{thisDir}/haskell/05-divide-by-zero/')

def test_haskell04():
    expectFail(f'python3 {checkScript} {checkScriptArgs} haskell --sheet 01',
            121, external=f'{haskellTestDir}/01', submissionDir=f'{haskellTestDir}/solutions/01')

def test_haskell05():
    expectOk(f'python3 {checkScript} {checkScriptArgs} haskell --sheet 03',
            external=f'{haskellTestDir}/03', submissionDir=f'{haskellTestDir}/solutions/03')

def test_haskell06():
    expectOk(f'python3 {checkScript} {checkScriptArgs} haskell --sheet 04',
            external=f'{haskellTestDir}/04', submissionDir=f'{haskellTestDir}/solutions/04')

def test_haskell07():
    expectOk(f'python3 {checkScript} {checkScriptArgs} haskell --sheet 05',
            external=f'{haskellTestDir}/05', submissionDir=f'{haskellTestDir}/solutions/05')

def test_haskell08():
    expectOk(f'python3 {checkScript} {checkScriptArgs} haskell --sheet 06',
            external=f'{haskellTestDir}/06', submissionDir=f'{haskellTestDir}/solutions/06')

def test_haskell09():
    # Sheet 06 again, but with a nested solution directory
    with tempDir(dir=haskellTestDir) as d:
        cp(f'{haskellTestDir}/solutions/06', pjoin(d, 'solution'))
        expectOk(f'python3 {checkScript} {checkScriptArgs} haskell --sheet 06',
                external=f'{haskellTestDir}/06', submissionDir=pjoin(haskellTestDir, basename(d)))
