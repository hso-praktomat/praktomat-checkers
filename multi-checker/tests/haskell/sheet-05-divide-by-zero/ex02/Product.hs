module Product where

import Test.HUnit
import Control.Monad.Reader

-- Beispielwerte
-- 1 Euro kostet 1,14 Dollar
-- 1 Euro kostet 1,05 CHF

data Config = Config { dollarRate :: Double, chfRate :: Double }

data Price
  = PriceEuro Double
  | PriceDollar Double
  | PriceCHF Double

data Product
  = Product
  { productName :: String
  , productQuantity :: Int
  , productSinglePrice :: Price
  }

data Invoice
  = Invoice
  { invoiceCustomer :: String
  , invoiceProducts :: [Product]
  }

sampleInvoice :: Invoice
sampleInvoice =
  Invoice
  { invoiceCustomer = "Stefan Wehr"
  , invoiceProducts = [p1, p2]
  }
  where
    p1 = Product "Feinstimmer Geige" 2 (PriceDollar 9.1086)
    p2 = Product "HX Effects" 1 (PriceCHF 523.95)

formatInvoice :: Invoice -> Reader Config String
formatInvoice invoice = do
  prods <- mapM formatProduct (invoiceProducts invoice)
  pure (invoiceCustomer invoice ++ "\n\n" ++
        unlines prods)

formatProduct :: Product -> Reader Config String
formatProduct prod = do
  price <- convertPrice (productSinglePrice prod)
  pure (productName prod ++ " (" ++ show (productQuantity prod) ++ "x) " ++
       show price ++ " EUR")

convertPrice :: Price -> Reader Config Double
convertPrice price =
  case price of
    PriceEuro e -> pure e
    PriceDollar d -> do
      r <- asks dollarRate
      pure (d / r)
    PriceCHF c -> do
      r <- asks chfRate
      pure (c / r)

-- Tests
allTests :: Test
allTests = TestList [
  ]
