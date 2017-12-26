###############################################################################
# sets up catan decks, resource and development
###############################################################################
from chance import *

class Card(object):
    def __init__(self, name):
        self.name = name.upper()

    def __eq__(self, other):
        return (isinstance(other, Card) and
                self.name == other.name)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

class Deck(object):
    # create deck of catan cards
    resourceCards = ["Wheat", "Rock", "Brick", "Sheep", "Lumber"]
    foundationCards = ["Vp", "Knight", "RoadBuilding", "Steal"]
    resourceDeck = []
    foundationDeck = []

    def createDeck(self, name):
        if self.name == "RESOURCE":
            for card in Deck.resourceCards:
                for i in range(19):
                    Deck.resourceDeck.append(Card(card))
        elif self.name == "FOUNDATION":
            for card in Deck.foundationCards:
                for i in range(13):
                    Deck.foundationDeck.append(Card(card))

    def __init__(self, name):
        self.name = name.upper()
        Deck.createDeck(self, name)


def createResourceDeck(deck):
    newDeck = []
    for card in deck.resourceCards:
        for i in range(19):
            newDeck.append(card)
    for card in deck.foundationDeck:
        for i in range(13):
            newDeck.append(card)
    return newDeck

def createFoundationDeck(deck):
    newDeck = []
    for card in deck.foundationCards:
        for i in range(13):
            newDeck.append(card)
    return newDeck


class DeckHold(object): pass
deck = DeckHold()
def init(deck=deck):
    deck.resourceCards = ["Wheat", "Rock", "Brick", "Sheep", "Lumber"]
    deck.foundationCards = ["VP", "Knight", "Roads", "Steal"]
    deck.resourceDeck = { "Wheat":19,
                          "Rock":19,
                          "Brick":19,
                          "Sheep":19,
                          "Lumber":19
                          }
    deck.foundationDeck = randomList(createFoundationDeck(deck))
    deck.hexes = { "Desert":1,
                   "Wheat": 4,
                   "Rock": 3,
                   "Brick": 3,
                   "Sheep": 4,
                   "Lumber": 4,
                   }
    deck.hexValues = { 2:1,
                       3:2,
                       4:2,
                       5:2,
                       6:2,
                       8:2,
                       9:2,
                       10:2,
                       11:2,
                       12:1,
                       }


def updateHand(d):
    for key in d:
        myhand[key] += d[key]
        deck.resourceDeck[key] -= d[key]
        if deck.resourceDeck[key] < 0:
            myhand[key] += deck.resourceDeck[key]
            deck.resourceDeck[key] = 0










