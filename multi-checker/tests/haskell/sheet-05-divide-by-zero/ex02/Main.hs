module Main where

import Product (allTests)
import Test.HUnit (runTestTTAndExit)

main :: IO ()
main = runTestTTAndExit allTests
