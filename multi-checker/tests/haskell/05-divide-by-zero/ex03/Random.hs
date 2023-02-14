module Random where

import Test.HUnit hiding (State)
import Control.Monad.State.Lazy

type Random a = State Integer a

fresh :: Random Integer
fresh = do
  x <- get
  let next = (6364136223846793005 * x + 1442695040888963407) `mod` 2^64
  put next
  return next

runPRNG :: Random a -> Integer -> a
runPRNG random seed =
    fst (runState random seed)

threeRandomNumbers :: Random [Integer]
threeRandomNumbers = do
  r1 <- fresh
  r2 <- fresh
  r3 <- fresh
  pure [r1, r2, r3]

assignment1 :: IO ()
assignment1 = print (runPRNG action 1)
  where
    action = do
      r1 <- fresh
      r2 <- fresh
      r3 <- fresh
      return [r1, r2, r3]

-- Tests
allTests :: Test
allTests = TestList [
  ]
