import asyncio
import os
import sys
import time
from argparse import ArgumentParser, Namespace
from multiprocessing import Pipe, Process, Manager, Pool
from multiprocessing.connection import Connection
from multiprocessing.pool import ThreadPool
from threading import Thread
from typing import List, Dict

from Joc import remote_start_app, remote_start_app_with_word
from Jucator import play

import yaml

GUESS_FILE = "solutii.yaml"


async def test():
    print(2)


def calculate_words(words: List[str], start_index: int, dictionary: Dict[str, List[str]],
                    extra_arguments: Dict[str, any]):
    connection1, connection2 = Pipe(duplex=True)
    game_process = Process(target=remote_start_app_with_word, args=(words, start_index, connection1),
                           kwargs=extra_arguments)
    game_process.start()
    for index in range(start_index, len(words), extra_arguments['calculate_step']):
        word: str = words[index]
        player = Process(target=play, args=(words, connection2), kwargs={'log': False})
        player.start()
        player.join()
        guess_list: List[str] = connection2.recv()
        if guess_list[len(guess_list) - 1] != word:
            raise Exception("Synchronization failed")
        end_time = time.perf_counter()
        dictionary[word] = guess_list
        print(f"Thread #{start_index + 1}: Word {word} took {len(guess_list)} guesses {guess_list}!")
    game_process.join()


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser(
        prog="Wordle",
        description="Wordle Game & Solver",
        epilog="Made by Deaconescu Mario, Miu Tudor, and Berbece David"
    )
    parser.add_argument("-a", "--all", action='store_true')
    parser.add_argument("-m", "--manual")
    parser.add_argument("-t", "--threads", default=1)
    parser.add_argument("-q", "--quit", action='store_true')
    args: Namespace = parser.parse_args()
    word_list: List[str]
    with open("cuvinte_wordle.txt") as f_cuvinte:
        word_list = [word[:5] for word in list(f_cuvinte)]
    number_of_threads: int = int(args.threads)
    arguments: Dict[str, int] = {'calculate_step': number_of_threads if args.all else 0}
    if args.all:
        arguments['auto_quit'] = True
        manager = Manager()
        word_dictionary: Dict[str, List[str]] = manager.dict()
        with ThreadPool(processes=number_of_threads) as pool:
            result = pool.starmap_async(calculate_words, [(word_list, thread, word_dictionary, arguments) for thread in
                                                          range(number_of_threads)])
            seconds_elapsed = 1
            inactive_seconds = 0
            time.sleep(1)
            last_remaining_words: int = 0
            while not result.ready():
                words_per_second = len(word_dictionary) / seconds_elapsed
                remaining_words = len(word_list) - len(word_dictionary)
                if last_remaining_words == remaining_words:
                    inactive_seconds += 1
                else:
                    inactive_seconds = 0
                    last_remaining_words = remaining_words
                if inactive_seconds == 2:
                    break
                if words_per_second == 0:
                    seconds_left: int = 0
                else:
                    seconds_left: int = int(remaining_words // words_per_second)
                print("=======================")
                print(f"{(len(word_dictionary) / len(word_list) * 100):.2f}% complete! ({seconds_left} seconds remaining)")
                print("=======================")
                seconds_elapsed += 1
                time.sleep(1)
            pool.close()
        unprocessed_words: List[str] = []
        arguments['calculate_step'] = 0
        arguments['auto_quit'] = True
        for word in word_list:
            if word not in word_dictionary:
                unprocessed_words.append(word)
        for word in unprocessed_words:
            connection1, connection2 = Pipe(duplex=True)
            game = Process(target=remote_start_app_with_word,
                           args=(word_list, word_list.index(word), connection1), kwargs=arguments)
            player = Process(target=play, args=(word_list, connection2))
            game.start()
            player.start()
            player.join()
            game.join()
            guess_list: List[str] = connection2.recv()
            word_dictionary[word] = guess_list
            print(f"Calculating remaining words: {(len(word_dictionary) / len(word_list) * 100):.2f}% complete!")
        with open(GUESS_FILE, "w") as file:
            ordered_words = sorted(word_dictionary.items(), key=lambda pair: pair[0])
            for word, guesses in ordered_words:
                file.write(f"{word}: {guesses}\n")
    else:
        connection1, connection2 = Pipe(duplex=True)
        if args.manual:
            game = Process(target=remote_start_app_with_word,
                           args=(word_list, word_list.index(args.manual), connection1), kwargs=arguments)
        else:
            game = Process(target=remote_start_app, args=(word_list, connection1), kwargs=arguments)
        player = Process(target=play, args=(word_list, connection2))
        game.start()
        player.start()
        game.join()
        player.join()
        print(connection2.recv())
