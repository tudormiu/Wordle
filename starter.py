import os
import sys
import time
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
    parser.add_argument("-m", "--manual")
    parser.add_argument("-q", "--quit", action='store_true')
    args: Namespace = parser.parse_args()
    connection1, connection2 = Pipe(duplex=True)
    word_list: List[str]
    with open("cuvinte_wordle.txt") as f_cuvinte:
        word_list = [word[:5] for word in list(f_cuvinte)]
    arguments: Dict[str, bool] = {'auto_quit': args.quit, 'calculate_all': True if args.all else False}
    if args.all:
        try:
            guesses: Dict[str, int] = {}
            if os.path.isfile(GUESS_FILE):
                with open(GUESS_FILE, "r") as file:
                    temp = yaml.safe_load(file)
                    if temp is not None:
                        guesses = temp
            calculated_words = len(guesses)
            game = Process(target=remote_start_app_with_word, args=(word_list, calculated_words, connection1), kwargs=arguments)
            game.start()
            start_time = time.perf_counter()
            for word in word_list[calculated_words:]:
                player = Process(target=play, args=(word_list, connection2), kwargs={'log': False})
                player.start()
                player.join()
                number_of_guesses = connection2.recv()
                end_time = time.perf_counter()
                guesses[word] = number_of_guesses
                print(f"Word {word} took {number_of_guesses} guesses! ({end_time - start_time} seconds)")
                start_time = end_time
            game.join()
            with open("guesses.yaml", "w") as file:
                yaml.dump(guesses, file)
        except KeyboardInterrupt:
            with open("guesses.yaml", "w") as file:
                yaml.dump(guesses, file)
            sys.exit(1)
    else:
        if args.manual:
            game = Process(target=remote_start_app_with_word, args=(word_list, word_list.index(args.manual), connection1), kwargs=arguments)
        else:
            game = Process(target=remote_start_app, args=(word_list, connection1), kwargs=arguments)
        player = Process(target=play, args=(word_list, connection2))
        game.start()
        player.start()
        game.join()
        player.join()
        print(connection2.recv())

