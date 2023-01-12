module Main where

import Random (allTests)
import Test.HUnit (runTestTTAndExit)

main :: IO ()
main = runTestTTAndExit allTests
