import os
import sys
from argparse import ArgumentParser, Namespace
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import List, Dict

from Joc import remote_start_app, remote_start_app_with_word
from Jucator import play

import yaml

GUESS_FILE = "guesses.yaml"

if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser(
        prog="Wordle",
        description="Wordle Game & Solver",
        epilog="Made by Deaconescu Mario, Miu Tudor, and Berbece David"
    )
    parser.add_argument("-a", "--all", action='store_true')
    parser.add_argument("-d", "--debug", action='store_true')
    args: Namespace = parser.parse_args()
    connection1, connection2 = Pipe(duplex=True)
    word_list: List[str]
    with open("cuvinte_wordle.txt") as f_cuvinte:
        word_list = list(f_cuvinte)
    if args.all:
        try:
            guesses: Dict[str, int] = {}
            if os.path.isfile(GUESS_FILE):
                with open(GUESS_FILE, "r") as file:
                    guesses = yaml.safe_load(file)
            calculated_words = len(guesses)
            for word in word_list[calculated_words:]:
                game = Process(target=remote_start_app_with_word, args=(word_list, word, connection1))
                player = Process(target=play, args=(word_list, connection2))
                game.start()
                player.start()
                game.join()
                player.join()
                number_of_guesses = connection1.recv()
                guesses[word[:5]] = number_of_guesses
            with open("guesses.yaml", "w") as file:
                yaml.dump(guesses, file)
        except KeyboardInterrupt:
            with open("guesses.yaml", "w") as file:
                yaml.dump(guesses, file)
            sys.exit(1)
    else:
        game = Process(target=remote_start_app, args=(word_list, connection1))
        player = Process(target=play, args=(word_list, connection2))
        game.start()
        player.start()
        game.join()
        player.join()
