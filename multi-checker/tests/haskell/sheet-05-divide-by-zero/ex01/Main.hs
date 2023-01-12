module Main where

import Exp (allTests)
import Test.HUnit (runTestTTAndExit)

main :: IO ()
main = runTestTTAndExit allTests
