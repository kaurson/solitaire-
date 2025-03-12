CARD_NAMES = [
    '10_C', '10_D', '10_H', '10_S',
    '2_C',  '2_D',  '2_H',  '2_S',
    '3_C',  '3_D',  '3_H',  '3_S',
    '4_C',  '4_D',  '4_H',  '4_S',
    '5_C',  '5_D',  '5_H',  '5_S',
    '6_C',  '6_D',  '6_H',  '6_S',
    '7_C',  '7_D',  '7_H',  '7_S',
    '8_C',  '8_D',  '8_H',  '8_S',
    '9_C',  '9_D',  '9_H',  '9_S',
    'A_C',  'A_D',  'A_H',  'A_S',
    'J_C',  'J_D',  'J_H',  'J_S',
    'K_C',  'K_D',  'K_H',  'K_S',
    'Q_C',  'Q_D',  'Q_H',  'Q_S'
]

RANK_MAP = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 11,
    'Q': 12,
    'K': 13
}

def parse_card_by_index(idx):
    """
    Given an index (0..51), return (rank_value, suit, card_str).
    E.g. parse_card_by_index(0) -> (10, 'C', '10_C').
    """
    card_str = CARD_NAMES[idx]
    rank_str, suit = card_str.split('_')
    rank_val = RANK_MAP[rank_str]
    return (rank_val, suit, card_str)

def parse_card_by_name(card_str):
    """
    Given a string like '9_S', return (rank_value, suit, card_str).
    """
    rank_str, suit = card_str.split('_')
    rank_val = RANK_MAP[rank_str]
    return (rank_val, suit, card_str)

def color_of_suit(suit):
    """Return 'black' for clubs/spades, 'red' for hearts/diamonds."""
    return 'black' if suit in ('C', 'S') else 'red'

def is_opposite_color(card1, card2):
    """Return True if the two cards have opposite color suits."""
    _, suit1, _ = card1
    _, suit2, _ = card2
    return color_of_suit(suit1) != color_of_suit(suit2)

class SolitaireGame:
    def __init__(self):
        """
        We do NOT track a full deck here.
        Instead, we rely on camera input to update:
          - The tableau: a list of lists (each list is a column, each element is a card tuple).
          - The foundation: a dict with suits as keys and lists of card tuples.
          - The top deck card: stored in self.top_card (a card tuple or None).
        """
        self.tableau = []
        self.foundation = {'C': [], 'D': [], 'H': [], 'S': []}
        self.top_card = None

    def update_from_camera(self, tableau_data, foundation_data, top_card_str=None):
        """
        Update game state from camera data.
          - tableau_data: a list of lists, e.g. [['10_C'], ['4_D', '3_S'], ...]
            (each inner list represents a tableau column; last element is considered the top)
          - foundation_data: a dict mapping suits to lists of card strings, e.g. {'C': [], 'D': ['A_D'], ...}
          - top_card_str: a string like '9_S' for the deck's top card; if None, then no card.
        """
        # Update tableau
        self.tableau = [
            [parse_card_by_name(card_name) for card_name in column]
            for column in tableau_data
        ]
        # Update foundation
        self.foundation = {suit: [parse_card_by_name(c) for c in cards] for suit, cards in foundation_data.items()}
        # Update the top deck card
        self.top_card = parse_card_by_name(top_card_str) if top_card_str else None

    # --- VALIDATION FUNCTIONS ---

    def can_move_to_foundation(self, card):
        """
        A card can be moved to the foundation if:
          - The foundation pile for its suit is empty and the card is an Ace, OR
          - The top card of the foundation pile has a rank that is one less than the card's rank.
        """
        rank, suit, _ = card
        stack = self.foundation[suit]
        if not stack:
            return (rank == 1)
        else:
            top_rank, _, _ = stack[-1]
            return (rank == top_rank + 1)

    def can_move_to_tableau(self, card, tableau_stack):
        """
        For the tableau:
          - If the tableau stack is empty, only a King can be placed (commonly),
            though you can adjust this rule.
          - If not empty, the card's rank must be one less than the top card's rank
            and the colors must be opposite.
        """
        rank, suit, _ = card
        if not tableau_stack:
            return (rank == 13)  # King is 13
        else:
            top_rank, top_suit, _ = tableau_stack[-1]
            return (rank == (top_rank - 1) and is_opposite_color(card, tableau_stack[-1]))

    # --- MOVE FUNCTIONS ---

    def move_top_card_to_foundation(self):
        """
        If the current top deck card can move to the foundation, do so.
        """
        if self.top_card and self.can_move_to_foundation(self.top_card):
            _, suit, _ = self.top_card
            self.foundation[suit].append(self.top_card)
            self.top_card = None
            return True
        return False

    def move_top_card_to_tableau(self, tableau_index):
        """
        If the current top deck card can be placed on the specified tableau column, do so.
        """
        if self.top_card and 0 <= tableau_index < len(self.tableau):
            if self.can_move_to_tableau(self.top_card, self.tableau[tableau_index]):
                self.tableau[tableau_index].append(self.top_card)
                self.top_card = None
                return True
        return False

    def move_tableau_to_foundation(self, tableau_index):
        """
        Move the top card from the given tableau column to the foundation, if valid.
        """
        if 0 <= tableau_index < len(self.tableau) and self.tableau[tableau_index]:
            card = self.tableau[tableau_index][-1]
            if self.can_move_to_foundation(card):
                _, suit, _ = card
                self.foundation[suit].append(self.tableau[tableau_index].pop())
                return True
        return False

    def move_tableau_to_tableau(self, from_index, to_index):
        """
        Move the top card from one tableau column to another, if valid.
        """
        if (0 <= from_index < len(self.tableau) and 0 <= to_index < len(self.tableau)
                and from_index != to_index and self.tableau[from_index]):
            card = self.tableau[from_index][-1]
            if self.can_move_to_tableau(card, self.tableau[to_index]):
                self.tableau[to_index].append(self.tableau[from_index].pop())
                return True
        return False

    # --- MOVE SELECTION ---

    def find_best_move(self):
        """
        Naively checks for a valid move in the following order:
          1. Top deck card to foundation.
          2. Top deck card to a tableau column.
          3. A tableau's top card to the foundation.
          4. A tableau-to-tableau move.
        Returns a tuple indicating the move:
          ("top_card_to_foundation",)
          ("top_card_to_tableau", tableau_index)
          ("tableau_to_foundation", tableau_index)
          ("tableau_to_tableau", from_index, to_index)
        or None if no move is found.
        """
        # 1. Top deck card to foundation.
        if self.top_card and self.can_move_to_foundation(self.top_card):
            return ("top_card_to_foundation",)
        
        # 2. Top deck card to tableau.
        if self.top_card:
            for t_idx in range(len(self.tableau)):
                if self.can_move_to_tableau(self.top_card, self.tableau[t_idx]):
                    return ("top_card_to_tableau", t_idx)
        
        # 3. Tableau to foundation.
        for t_idx in range(len(self.tableau)):
            if self.tableau[t_idx]:
                top_t_card = self.tableau[t_idx][-1]
                if self.can_move_to_foundation(top_t_card):
                    return ("tableau_to_foundation", t_idx)
        
        # 4. Tableau to tableau.
        for from_idx in range(len(self.tableau)):
            if not self.tableau[from_idx]:
                continue
            card = self.tableau[from_idx][-1]
            for to_idx in range(len(self.tableau)):
                if from_idx == to_idx:
                    continue
                if self.can_move_to_tableau(card, self.tableau[to_idx]):
                    return ("tableau_to_tableau", from_idx, to_idx)
        
        return None

# --- EXAMPLE USAGE ---

if __name__ == "__main__":
    game = SolitaireGame()

    # Simulate camera data:
    # The tableau data: each sublist represents a tableau column.
    # (Assume the last element in each list is the top card of that column.)
    camera_tableau = [
        ['3_H'],         # Column 0
        [],              # Column 1 is empty
        ['10_D', '9_S']  # Column 2: 10_D at bottom, 9_S on top
    ]
    # Foundation data: mapping suits to the cards in their foundation piles.
    camera_foundation = {
        'C': [],
        'D': ['A_D'],  # For example, the diamond foundation already has the Ace of Diamonds.
        'H': [],
        'S': []
    }
    # The top card of the deck, as seen by the camera.
    camera_top_card = 'K_C'

    # Update game state with the camera input.
    game.update_from_camera(camera_tableau, camera_foundation, camera_top_card)

    print("Initial state from camera:")
    print("Tableau:")
    for idx, column in enumerate(game.tableau):
        print(f"  Column {idx}: {[card[2] for card in column]}")
    print("Foundation:", {suit: [card[2] for card in cards] for suit, cards in game.foundation.items()})
    print("Top deck card:", game.top_card[2] if game.top_card else None)

    # Find and print the best move.
    move = game.find_best_move()
    print("\nBest move:", move)

    # Execute the move.
    if move:
        if move[0] == "top_card_to_foundation":
            game.move_top_card_to_foundation()
        elif move[0] == "top_card_to_tableau":
            _, t_idx = move
            game.move_top_card_to_tableau(t_idx)
        elif move[0] == "tableau_to_foundation":
            _, t_idx = move
            game.move_tableau_to_foundation(t_idx)
        elif move[0] == "tableau_to_tableau":
            _, from_idx, to_idx = move
            game.move_tableau_to_tableau(from_idx, to_idx)

    print("\nState after move:")
    print("Tableau:")
    for idx, column in enumerate(game.tableau):
        print(f"  Column {idx}: {[card[2] for card in column]}")
    print("Foundation:", {suit: [card[2] for card in cards] for suit, cards in game.foundation.items()})
    print("Top deck card:", game.top_card[2] if game.top_card else None)

    # After the move, your camera system would update with the new visible state.
    # For example, if the top card was consumed, a new card might appear:
    if game.top_card is None:
        # Simulate a new top card, e.g. '2_H'
        game.update_from_camera(camera_tableau, camera_foundation, top_card_str='2_H')
    print("\nUpdated state from camera after new card:")
    print("Top deck card:", game.top_card[2] if game.top_card else None)
