module Exp where

import Test.HUnit

data Exp = ExpAdd Exp Exp
         | ExpMult Exp Exp
         | ExpDiv Exp Exp
         | Const Integer

eval1 :: Exp -> Maybe Integer
eval1 = eval2

eval3 :: Exp -> Maybe Integer
eval3 = eval2

eval2 :: Exp -> Maybe Integer
eval2 exp =
  case exp of
    ExpAdd l r -> bin (+) l r
    ExpMult l r -> bin (*) l r
    ExpDiv l r -> do
      l' <- eval2 l
      r' <- eval2 r
      --if r' == 0 then Nothing else pure (l' `div` r')
      pure (l' `div` r') -- ERROR!
    Const i -> pure i
  where
    bin f l r = do
      l' <- eval2 l
      r' <- eval2 r
      pure (f l' r')

-- Tests
allTests :: Test
allTests = TestList [
  ]
