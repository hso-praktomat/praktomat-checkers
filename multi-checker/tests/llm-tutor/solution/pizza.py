from wypp import *

# Die Größe einer Pizza ist eine von 'Normal' oder 'Groß'.
type Größe = Literal['normal', 'groß']

# Eine Pizza besteht aus folgenden Eigenschaften:
# - Größe (normal oder groß)
# - folgenden Zutaten:
# - - Oliven
# - - Pilze
# - - Salami
# - - Käse
# Die Zutaten können alle optional gewählt werden.
@record
class Pizza:
    größe: Größe
    oliven: bool = False
    pilze: bool = False
    salami: bool = False
    käse: bool = False


# Berechnet den Preis einer Pizza.
# Je nach Zutat und Größe werden dabei verschiedene Aufpreise berechnet
# Eingabe: Pizza
# Ausgabe: Preis (float)
def calcPizzaPreis(pizza: Pizza) -> float:
    preis = 0
    if pizza.oliven:
        preis = preis + 0.5
    if pizza.pilze:
        preis = preis +  0.4
    if pizza.salami:
        preis = preis +  0.45
    if pizza.käse:
        preis = preis +  0.55
    # 10% Aufpreis auf Zutaten für große Pizzen
    if pizza.größe == 'groß':
        preis = preis * 1.1
        preis = preis +  2.5 # Grundpreis für groß
    else:
        preis = preis +  2   # Grundpreis für normal

    return preis

check(calcPizzaPreis(Pizza('normal', True, True, True, True)), 3.9)
check(calcPizzaPreis(Pizza('normal', True, True, True)), 3.35)
check(calcPizzaPreis(Pizza('normal', True, True)), 2.9)
check(calcPizzaPreis(Pizza('normal', True)), 2.5)
check(calcPizzaPreis(Pizza('normal')), 2)

check(calcPizzaPreis(Pizza('groß', True, True, True, True)), 4.59)
check(calcPizzaPreis(Pizza('groß', True, True, True)), 3.985)
check(calcPizzaPreis(Pizza('groß', True, True)), 3.49)
check(calcPizzaPreis(Pizza('groß', True)), 3.05)
check(calcPizzaPreis(Pizza('groß')), 2.5)
