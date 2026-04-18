import csv
import logging
import multiprocessing
import os
import random
import shutil
from src import Game

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s  %(message)s',
    force=True
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'output')

NUM_WORKERS = 4
ITERATIONS = 5397763
PLAYERS = 4
RANDOM_SEED = 0


def worker_job(worker_index, iterations, num_players, seed_base, output_dir):
    worker_seed = seed_base + worker_index
    random.seed(worker_seed)
    worker_output = os.path.join(output_dir, f'worker_{worker_index}')
    game = Game(output_dir=worker_output)

    for i in range(iterations):
        game.run(num_players=num_players)
        if (i + 1) % 50000 == 0:
            logging.info(f"[worker {worker_index}] {i + 1} out of {iterations}")

    return worker_output


def merge_worker_csvs(output_dir, worker_dirs):
    os.makedirs(output_dir, exist_ok=True)
    filenames = ['game_data_house.csv', 'game_data_player.csv']

    for filename in filenames:
        final_path = os.path.join(output_dir, filename)
        with open(final_path, 'w', newline='') as outfile:
            writer = None
            for worker_dir in worker_dirs:
                worker_file = os.path.join(worker_dir, filename)
                if not os.path.exists(worker_file):
                    continue

                with open(worker_file, 'r', newline='') as infile:
                    reader = csv.reader(infile)
                    header = next(reader, None)
                    if header is None:
                        continue
                    if writer is None:
                        writer = csv.writer(outfile)
                        writer.writerow(header)
                    for row in reader:
                        writer.writerow(row)


def remove_worker_dirs(worker_dirs):
    for worker_dir in worker_dirs:
        if os.path.isdir(worker_dir):
            shutil.rmtree(worker_dir)


def split_iterations(total, parts):
    base = total // parts
    remainder = total % parts
    return [base + (1 if i < remainder else 0) for i in range(parts)]


if __name__ == '__main__':
    seed = random.randint(1000, 9999)
    seed_base = RANDOM_SEED if RANDOM_SEED != 0 else seed
    logging.info(f"Random Seed: {seed}\n")

    iterations_by_worker = split_iterations(ITERATIONS, NUM_WORKERS)
    worker_args = [
        (idx, iterations_by_worker[idx], PLAYERS, seed_base, DATA_DIR)
        for idx in range(NUM_WORKERS)
    ]

    with multiprocessing.Pool(processes=NUM_WORKERS) as pool:
        worker_dirs = pool.starmap(worker_job, worker_args)

    merge_worker_csvs(DATA_DIR, worker_dirs)
    remove_worker_dirs(worker_dirs)
    logging.info(f"Completed {ITERATIONS} iterations across {NUM_WORKERS} workers.")
