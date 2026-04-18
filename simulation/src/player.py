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