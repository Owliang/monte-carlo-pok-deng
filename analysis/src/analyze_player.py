import pandas as pd
import re

# Set display options to see more rows
pd.options.display.max_rows = 500

# Define the card faces and their order
faces = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
face_rank = {f: i for i, f in enumerate(faces)}

def normalize_initial_cards(card_str):
    if pd.isna(card_str) or not isinstance(card_str, str):
        return card_str

    cards = [c.strip() for c in card_str.split(',')]
    if len(cards) != 2:
        return card_str

    c1_face, c1_suit = cards[0][:-1], cards[0][-1]
    c2_face, c2_suit = cards[1][:-1], cards[1][-1]

    if face_rank[c1_face] <= face_rank[c2_face]:
        high_f, low_f = c1_face, c2_face
    else:
        high_f, low_f = c2_face, c1_face

    suffix = 's' if c1_suit == c2_suit else 'o'
    return f"{high_f}{low_f}{suffix}"

file_path = r'C:\Users\owlia\OneDrive\Desktop\game_data_house.csv'
try:
    df = pd.read_csv(file_path)

    # Apply normalization to cards
    df['hand_shorthand'] = df['initial_cards'].apply(normalize_initial_cards)

    # Create a unified action column
    def unify_actions(row):
        act1 = str(row['action_type'])
        act2 = row['action_type_2']

        # Special case for combined resolutions
        if (act1 == 'RESOLVE_3_CARD' and act2 == 'RESOLVE_2_CARD') or (act1 == 'RESOLVE_ALL'):
            return 'RESOLVE_ALL'

        # If act2 is NaN, return only act1
        if pd.isna(act2):
            return act1

        return f"{act1}_THEN_{act2}"

    df['unified_action'] = df.apply(unify_actions, axis=1)

    # Grouping using the unified action column
    grouped = df.groupby(['hand_shorthand', 'unified_action'], dropna=False).agg(
        avg_result=('result', 'mean'),
        avg_deng=('deng', 'mean'),
        count=('result', 'size')
    ).reset_index()

    # Sort by hand_shorthand then unified_action
    sorted_results = grouped.sort_values(by=['hand_shorthand', 'unified_action'])

    print(sorted_results)
except FileNotFoundError:
    print(f"Error: The file at {file_path} was not found.")