from testUtils import *

haskellTestDir = f'{praktomatTests}/haskell-advanced-prog'
haskellTestDirLocal = f'{praktomatTestsLocal}/haskell-advanced-prog'

def test_haskell01():
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/02 haskell --sheet 02',
            external=f'{haskellTestDirLocal}/02', dir=f'{haskellTestDir}/solutions/02')

def test_haskell02():
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {thisDir}/haskell/02-no-file haskell --sheet 02',
            1, external=f'{haskellTestDirLocal}/02', dir=f'{thisDir}/haskell/02-no-file')

def test_haskell03():
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {thisDir}/haskell/05-divide-by-zero/ haskell --sheet 05',
            121, external=f'{haskellTestDirLocal}/05', dir=f'{thisDir}/haskell/05-divide-by-zero/')

def test_haskell04():
    expectFail(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/01 haskell --sheet 01',
            121, external=f'{haskellTestDirLocal}/01', dir=f'{haskellTestDir}/solutions/01')

def test_haskell05():
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/03 haskell --sheet 03',
            external=f'{haskellTestDirLocal}/03', dir=f'{haskellTestDir}/solutions/03')

def test_haskell06():
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/04 haskell --sheet 04',
            external=f'{haskellTestDirLocal}/04', dir=f'{haskellTestDir}/solutions/04')

def test_haskell07():
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/05 haskell --sheet 05',
            external=f'{haskellTestDirLocal}/05', dir=f'{haskellTestDir}/solutions/05')

def test_haskell08():
    expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {haskellTestDir}/solutions/06 haskell --sheet 06',
            external=f'{haskellTestDirLocal}/06', dir=f'{haskellTestDir}solutions/06')

def test_haskell09():
    # Sheet 06 again, but with a nested solution directory
    with tempDir(dir=haskellTestDirLocal) as d:
        cp(f'{haskellTestDirLocal}/solutions/06', pjoin(d, 'solution'))
        expectOk(f'python3 {checkScript} {checkScriptArgs} --submission-dir {pjoin(haskellTestDir, basename(d))} haskell --sheet 06',
                external=f'{haskellTestDirLocal}/06', dir=pjoin(haskellTestDir, basename(d)))
