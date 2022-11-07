import random
from argparse import ArgumentParser, Namespace
from Joc import WordleApp

if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser(
        prog="Wordle",
        description="Wordle Game & Solver",
        epilog="Made by Deaconescu Mario, Miu Tudor, and Berbece David"
    )
    parser.add_argument("mode", choices=['game', 'solver'])
    parser.add_argument("-m", "--manual")
    parser.add_argument("-d", "--debug", action='store_true')
    args: Namespace = parser.parse_args()
    with open("cuvinte_wordle.txt") as f_cuvinte:
        word_list = list(f_cuvinte)
    if args.mode == "game":
        correct_word: str
        if args.manual:
            correct_word = args.manual.upper()
        else:
            correct_word = word_list[random.randint(0, len(word_list))][0:5]
        if args.debug:
            print(f'Correct word: {correct_word}')
        WordleApp(word_list, correct_word).run()