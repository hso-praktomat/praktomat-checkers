module Main where

-- Aufgabe 1
countBy :: (a -> Bool) -> [a] -> Int
countBy _ [] = 0
countBy pred (x:xs)
  | pred x = 1 + countBy pred xs
  | otherwise = countBy pred xs

-- Aufgabe 2
fromTo :: Int -> Int -> [Int]
fromTo start end
  | start > end = []
  | otherwise = start : (fromTo (start+1) end)

-- Aufgabe 3
minBy :: (a -> Int) -> [a] -> a
minBy _ [] = error "empty list"
minBy _ [x] = x
minBy f (x:y:rest)
  | f x <= f y = minBy f (x:rest)
  | otherwise = minBy f (y:rest)

-- Aufgabe 4
allEven :: [Int] -> Bool
allEven = foldr (\i acc -> even i && acc) True

-- Aufgabe 5
conj :: [Bool] -> Bool
conj = foldl (\acc b -> acc && b) True

-- Aufgabe 6
data Food
  = Food
  { f_name :: String
  , f_size :: Int
  , f_sugar :: SugarContent
  }

data SugarContent
  = SugarTotal Double Double
  | SugarPer100 Double
  | SugarTrafficLight TrafficLight

data TrafficLight = Green | Yellow | Red

coke :: Food
coke = Food "Coca Cola" 500 (SugarTotal 25 25)

ritterSport :: Food
ritterSport = Food "Ritter Sport" 100 (SugarTotal 15.29 24.9)

pumpkin :: Food
pumpkin = Food "Kürbis" 1000 (SugarPer100 2.8)

cucumber :: Food
cucumber = Food "Gurke" 470 (SugarTrafficLight Green)

sugarTrafficLight :: Food -> TrafficLight
sugarTrafficLight food =
  case f_sugar food of
    SugarTotal x y -> trafficLightPer100 (100 * (x + y) / fromInteger (toInteger $ f_size food))
    SugarPer100 x -> trafficLightPer100 x
    SugarTrafficLight tl -> tl
  where
    trafficLightPer100 x =
      if x < 5 then Green else if x <= 22.5 then Yellow else Red

main :: IO ()
main = pure ()
