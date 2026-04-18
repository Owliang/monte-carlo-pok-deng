import random
import logging
import csv
import os
from deck import Deck
from action import Action, ActionType
from player import Player

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