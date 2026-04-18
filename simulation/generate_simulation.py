import logging
import os
import random
from simulation.src.game import Game

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s  %(message)s',
    force=True
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'output')

ITERATIONS = 100_000
PLAYERS = 4
RANDOM_SEED = 0

# Set a random seed for replication
seed = random.randint(1000, 9999)
random.seed(RANDOM_SEED if RANDOM_SEED != 0 else seed)
logging.info(f"Random Seed: {seed}\n")

# 3. Execution
if __name__ == "__main__":
    game = Game(output_dir=DATA_DIR)
    
    for i in range(ITERATIONS):
        game.run(num_players=PLAYERS)
        if (i + 1) % 50_000 == 0:
            logging.info(f"{i + 1} out of {ITERATIONS}")
