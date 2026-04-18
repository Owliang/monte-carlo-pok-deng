from .card import Card
from enum import Enum

class ActionType(Enum):
    HIT = 'HIT'
    STAY = 'STAY'
    RESOLVE_2_CARD = 'RESOLVE_2_CARD'
    RESOLVE_3_CARD = 'RESOLVE_3_CARD'
    RESOLVE_ALL = 'RESOLVE_ALL'
    HIT_RESOLVE_2_CARD = 'HIT_RESOLVE_2_CARD'
    HIT_RESOLVE_ALL = 'HIT_RESOLVE_ALL'

class Action:
    def __init__(self, action_type: ActionType, known_cards: list, index):
        if not isinstance(action_type, ActionType):
            raise ValueError("Action must be an instance of ActionType Enum.")
        if not isinstance(known_cards, list) or not all(isinstance(card, Card) for card in known_cards):
            raise ValueError("known_cards must be a list of Card objects.")

        self.action_type = action_type
        self.known_cards = known_cards
        self.index = index

    def __repr__(self):
        return f"Action[{self.index}]: {self.action_type.value} | Known cards: {sorted(self.known_cards)}"