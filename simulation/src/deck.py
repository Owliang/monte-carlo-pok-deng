import random
from .card import Card

class Deck:
    def __init__(self):
        self.cards = [Card(face, suit) for face in Card.VALID_FACES for suit in Card.VALID_SUITS]
        random.shuffle(self.cards)

    def draw(self, amount):
        if amount > len(self.cards):
            raise ValueError(f"Not enough cards in deck! Requested {amount}, but only {len(self.cards)} remain.")
        # Returns the first 'amount' cards and removes them from the list
        drawn_cards = self.cards[:amount]
        self.cards = self.cards[amount:]
        return drawn_cards

    def __repr__(self):
        return f"Deck of {len(self.cards)} cards"