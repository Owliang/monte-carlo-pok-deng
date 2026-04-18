import random
import logging
import csv
import os
from enum import Enum

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s  %(message)s',
    force=True
)

class Card:
    # face: 'A', '2', ..., '9', 'T', 'J', 'Q', 'K'
    VALID_FACES = {'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K'}
    # suit: 'c' (clubs), 'd' (diamonds), 'h' (hearts), 's' (spades)
    VALID_SUITS = {'c', 'd', 'h', 's'}

    # ANSI Color Codes
    COLORS = {
        'h': '\033[91m', # Bright Red
        'c': '\033[92m', # Bright Green
        'd': '\033[96m', # Bright Blue
        's': '\033[93m', # White
        'RESET': '\033[0m'
    }

    def __init__(self, face, suit):
        if str(face) not in self.VALID_FACES:
            raise ValueError(f"Invalid face: {face}. Must be one of {self.VALID_FACES}")
        if str(suit) not in self.VALID_SUITS:
            raise ValueError(f"Invalid suit: {suit}. Must be one of {self.VALID_SUITS}")

        self.face = str(face)
        self.suit = str(suit)

    def point(self):
        if self.face == 'A': return 1
        elif self.face in ('T', 'J', 'Q', 'K'): return 0
        else: return int(self.face)

    def sort_key(self):
        # Suit priority: c=0, d=1, h=2, s=3
        suit_order = {'c': 0, 'd': 1, 'h': 2, 's': 3}
        # Face priority: A=1, 2=2... T=10, J=11, Q=12, K=13
        face_order = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13}
        return (suit_order[self.suit], face_order[self.face])

    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.sort_key() < other.sort_key()

    def __repr__(self):
        color = self.COLORS.get(self.suit, '')
        reset = self.COLORS['RESET']
        return f"{color}{self.face}{self.suit}{reset}"
    
    def __str__(self):
        return f"{self.face}{self.suit}"

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

class Player:
    def __init__(self, initial_cards):
        if len(initial_cards) != 2:
            raise ValueError("initial_cards must contain exactly 2 cards.")
        self.initial_cards = initial_cards
        self._hit_card = []
        self.finish = False
        self.need_resolve_without_house_hit_card = False
        self.actions = []

    @property
    def hit_card(self):
        return self._hit_card

    @hit_card.setter
    def hit_card(self, cards):
        if not isinstance(cards, list):
            raise TypeError("hit_card must be a list.")
        if len(cards) > 1:
            raise ValueError("hit_card can contain at most 1 card.")
        self._hit_card = cards

    @property
    def hand(self):
        return self.initial_cards + self._hit_card

    def has_hit_card(self):
        return len(self.hit_card) == 1

    def has_action(self):
        return len(self.actions) > 0

    def _get_sorted_rank_indices(self, cards):
        # Map faces to indices for straight checking: A=0, 2=1, ..., T=9, J=10, Q=11, K=12
        rank_map = {'A':0, '2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7, '9':8, 'T':9, 'J':10, 'Q':11, 'K':12}
        return sorted([rank_map[card.face] for card in cards])

    def point(self, exclude_hit_card=False):
        cards = self.initial_cards if exclude_hit_card else self.hand
        n = len(cards)
        base_point = sum(card.point() for card in cards) % 10

        # 1. & 2. Check for Pok 9 and Pok 8 (2 cards only)
        if n == 2:
            if base_point == 9: return 109
            if base_point == 8: return 108

        # 3nd card conditions
        if n == 3:
            faces = [c.face for c in cards]
            suits = [c.suit for c in cards]
            indices = self._get_sorted_rank_indices(cards)

            is_flush = len(set(suits)) == 1
            is_trips = len(set(faces)) == 1
            is_pictures = all(f in ('J', 'Q', 'K') for f in faces)
            is_straight = (indices[2] - indices[0] == 2 and indices[1] - indices[0] == 1)

            if is_straight and is_flush: return 107
            if is_trips: return 106
            if is_pictures: return 105
            if is_straight: return 104
            if is_flush: return 103

        return base_point

    def deng(self, exclude_hit_card=False):
        cards = self.initial_cards if exclude_hit_card else self.hand
        n = len(cards)

        if n == 2:
            c1, c2 = cards
            if c1.suit == c2.suit or c1.face == c2.face:
                return 2
            return 1

        if n == 3:
            faces = [c.face for c in cards]
            suits = [c.suit for c in cards]
            indices = self._get_sorted_rank_indices(cards)

            is_flush = len(set(suits)) == 1
            is_trips = len(set(faces)) == 1
            is_pictures = all(f in ('J', 'Q', 'K') for f in faces)
            is_straight = (indices[2] - indices[0] == 2 and indices[1] - indices[0] == 1)

            if (is_straight and is_flush) or is_trips:
                return 5
            if is_pictures or is_straight or is_flush:
                return 3

        return 1

    def __repr__(self):
        initial_cards_str = " ".join(str(card) for card in sorted(self.initial_cards))
        hit_card_str = f" + {self.hit_card[0]}" if self.has_hit_card() else ""
        return f"Hand: {initial_cards_str}{hit_card_str} (Points: {self.point()}, Deng: {self.deng()})"

class Game:
    def __init__(self, output_dir='.'):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self, num_players):
        if num_players > 16:
            raise ValueError(f"Maximum 16 players allowed. Requested: {num_players}")

        # Create deck of cards
        deck = Deck()

        # Each player draws 2 cards initially
        self.players = [Player(deck.draw(2)) for _ in range(num_players)]
        self.house = Player(deck.draw(2))

        self.known_card = []
        self.action_index = 0

        # Check for Pok 8/9 in house
        if self.house.point() in (109, 108):
            self.resolve(self.players, self.house)
            return

        # Check for Pok 8/9 in players
        for i, player in enumerate(self.players):
            if player.point() in (109, 108):
                player.finish = True
                self.known_card.extend(player.hand)

        # Players take action, hit or stay
        for i, player in enumerate(self.players):
            if not player.finish:
                if random.random() < 0.5: # 50% chance to hit
                    player.hit_card = deck.draw(1)
                    player.actions.append(Action(ActionType.HIT, self.known_card[:], self.action_index))
                    self.action_index += 1
                else:
                    player.actions.append(Action(ActionType.STAY, self.known_card[:], self.action_index))
                    self.action_index += 1

        # Check if resolve player with 3 cards first is allowed.
        has_3_card_unfinish_player = False
        for player in self.players:
            if not player.finish and player.has_hit_card():
                has_3_card_unfinish_player = True
                break
        has_2_card_unfinish_player = False
        for player in self.players:
            if not player.finish and not player.has_hit_card():
                has_2_card_unfinish_player = True
                break
        is_resolve_3_card_first_allow = has_3_card_unfinish_player and has_2_card_unfinish_player

        # House takes action
        house_decision_roll = random.random()
        chance_configs = [0.25, 0.50, 0.75, 1.00] if is_resolve_3_card_first_allow else [0.50, 1.00, 0.00, 0.00]
        if house_decision_roll < chance_configs[0]: # resolve all
            self.house.actions.append(Action(ActionType.RESOLVE_ALL, self.known_card[:], self.action_index))
            self.action_index += 1
            self.resolve(self.players, self.house)
            return

        if house_decision_roll < chance_configs[1]: # hit, then resolve all
            self.house.actions.append(Action(ActionType.HIT_RESOLVE_ALL, self.known_card[:], self.action_index))
            self.action_index += 1
            self.house.hit_card = deck.draw(1)
            self.resolve(self.players, self.house)
            return

        if house_decision_roll < chance_configs[2]: # resolve 3 cards, then hit, then resolve 2 cards
            self.house.actions.append(Action(ActionType.RESOLVE_3_CARD, self.known_card[:], self.action_index))
            self.action_index += 1
            for player in self.players:
                if not player.finish and player.has_hit_card():
                    player.finish = True
                    player.need_resolve_without_house_hit_card = True
                    self.known_card.extend(player.hand)

            self.house.actions.append(Action(ActionType.HIT_RESOLVE_2_CARD, self.known_card[:], self.action_index))
            self.action_index += 1
            self.house.hit_card = deck.draw(1)
            self.resolve(self.players, self.house)
            return

        if house_decision_roll < chance_configs[3]: # resolve 3 cards, then resolve 2 cards
            self.house.actions.append(Action(ActionType.RESOLVE_3_CARD, self.known_card[:], self.action_index))
            self.action_index += 1
            for player in self.players:
                if not player.finish and player.has_hit_card():
                    player.finish = True
                    player.need_resolve_without_house_hit_card = True
                    self.known_card.extend(player.hand)

            self.house.actions.append(Action(ActionType.RESOLVE_2_CARD, self.known_card[:], self.action_index))
            self.action_index += 1
            self.resolve(self.players, self.house)
            return

        raise(SystemError("Invalid house decision roll"))

    def resolve_bet(self, players, house):
        if not isinstance(house, Player):
            raise ValueError("House must be a Player object.")
        if not isinstance(players, list) or len(players) == 0:
            raise ValueError("Players must be a non-empty list of Player objects.")

        results = []
        for player in players:
            if player.point() > house.point(player.need_resolve_without_house_hit_card):
                results.append(player.deng())
            elif player.point() < house.point(player.need_resolve_without_house_hit_card):
                results.append(-house.deng(player.need_resolve_without_house_hit_card))
            else:
                results.append(0)
        return results

    def resolve(self, players, house):
        results = self.resolve_bet(players, house)
        house_result = 0

        csv_filename_player = os.path.join(self.output_dir, 'game_data_player.csv')
        file_exists_player = os.path.isfile(csv_filename_player)
        with open(csv_filename_player, mode='a', newline='') as file:
            fieldnames = ['initial_cards', 'result', 'deng', 'point', 'hit_card', 'action_type', 'action_known_cards']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists_player:
                writer.writeheader()

            for i, result in enumerate(results):
                logging.debug(f"Player {i+1}")
                player = players[i]
                logging.debug(f"{player}")

                if player.has_action():
                    for action in player.actions:
                        logging.debug(f"{action}")

                logging.debug(f"Result: {result}\n")
                house_result -= result

                # Adding info for Monte Carlo
                data = {}
                data['initial_cards'] = ", ".join([str(c) for c in player.initial_cards])
                data['result'] = result
                data['deng'] = player.deng()
                data['point'] = player.point()
                data['hit_card'] = ", ".join([str(c) for c in player.hit_card]) if player.has_hit_card() else ''
                data['action_type'] = player.actions[0].action_type.value if player.has_action() else ''
                data['action_known_cards'] = ", ".join([str(c) for c in player.actions[0].known_cards]) if player.has_action() else ''

                writer.writerow(data)

        csv_filename_house = os.path.join(self.output_dir, 'game_data_house.csv')
        file_exists_house = os.path.isfile(csv_filename_house)
        with open(csv_filename_house, mode='a', newline='') as file:
            fieldnames = ['initial_cards', 'result', 'deng', 'point', 'hit_card', 'action_type', 'action_known_cards', 'action_type_2', 'action_known_cards_2']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            if not file_exists_house:
                writer.writeheader()

            logging.debug(f"House")
            logging.debug(f"{self.house}")
            if self.house.has_action():
                for action in self.house.actions:
                    logging.debug(f"{action}")
            logging.debug(f"Result: {house_result}")

            # Adding info for Monte Carlo
            data = {}
            data['initial_cards'] = ", ".join([str(c) for c in self.house.initial_cards])
            data['result'] = house_result
            data['deng'] = self.house.deng()
            data['point'] = self.house.point()
            data['hit_card'] = ", ".join([str(c) for c in self.house.hit_card]) if self.house.has_hit_card() else ''
            data['action_type'] = self.house.actions[0].action_type.value if self.house.has_action() else ''
            data['action_known_cards'] = ", ".join([str(c) for c in self.house.actions[0].known_cards]) if self.house.has_action() else ''
            data['action_type_2'] = self.house.actions[1].action_type.value if len(self.house.actions) == 2 else ''
            data['action_known_cards_2'] = ", ".join([str(c) for c in self.house.actions[1].known_cards]) if len(self.house.actions) == 2 else ''

            writer.writerow(data)








# Set a random seed for replication
# seed = random.randint(1000000000, 9999999999)
# random.seed(seed)
# logging.info(f"Random Seed: {seed}\n")

# Create and run the game
output_folder = r'C:\Users\owlia\OneDrive\Desktop'
game = Game(output_dir=output_folder)
n = 40000000
for i in range(n):
    game.run(num_players=4)
    if (i+1) % 50000 == 0:
        logging.info(f"{i+1} out of {n}")