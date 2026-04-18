import os
import pandas as pd
from datetime import datetime

# Set display options to see more rows
pd.options.display.max_rows = 500

# Define the card faces and their order
faces = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
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
        low_f, high_f = c1_face, c2_face
    else:
        low_f, high_f = c2_face, c1_face

    suffix = 's' if c1_suit == c2_suit else 'o'
    return f"{low_f}{high_f}{suffix}"


def unify_actions(row):
    act1 = row.get('action_type')
    act2 = row.get('action_type_2')

    if pd.isna(act1) or act1 is None:
        act1 = ''
    if pd.isna(act2) or act2 is None:
        act2 = ''

    act1 = str(act1).strip()
    act2 = str(act2).strip()

    if act1 == 'RESOLVE_3_CARD' and act2 == 'RESOLVE_2_CARD':
        return 'RESOLVE_ALL'

    if act1 == 'RESOLVE_ALL' and not act2:
        return 'RESOLVE_ALL'

    if not act2:
        return act1

    return f"{act1}_THEN_{act2}"


def get_input_file_path():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(repo_root, 'simulation', 'output', 'game_data_house.csv')


def get_output_file_path():
    output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f'analysis_house_{timestamp}.csv'
    return os.path.join(output_dir, filename)


def run():
    input_path = get_input_file_path()
    output_path = get_output_file_path()

    if not os.path.exists(input_path):
        raise FileNotFoundError(f'The file at {input_path} was not found.')

    df = pd.read_csv(input_path)

    df['card'] = df['initial_cards'].apply(normalize_initial_cards)
    df['action'] = df.apply(unify_actions, axis=1)

    grouped = (
        df.groupby(['card', 'action'], dropna=False)
        .agg(avg_return=('result', 'mean'), count=('result', 'size'))
        .reset_index()
    )

    sorted_results = grouped.sort_values(by=['card', 'avg_return'], ascending=[True, False])

    sorted_results.to_csv(output_path, index=False, columns=['card', 'action', 'avg_return', 'count'])
    print(f'Wrote analysis output to: {output_path}')


if __name__ == '__main__':
    run()