class Card:
    # face: 'A', '2', ..., '9', 'T', 'J', 'Q', 'K'
    VALID_FACES = {'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K'}
    # suit: 'c' (clubs), 'd' (diamonds), 'h' (hearts), 's' (spades)
    VALID_SUITS = {'c', 'd', 'h', 's'}

    # ANSI Color Codes
    COLORS = {
        'h': '\033[91m', # Red
        'c': '\033[92m', # Green
        'd': '\033[96m', # Blue
        's': '\033[93m', # Yellow
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