from collections import OrderedDict
from typing import Dict, List

import yaml

GUESS_FILE = "solutii.yaml"

if __name__ == "__main__":
    with open(GUESS_FILE, "r") as file:
        calculated_list: Dict[str, List[str]] = yaml.safe_load(file)
    with open("cuvinte_wordle.txt") as f_cuvinte:
        word_list = [word[:5] for word in list(f_cuvinte)]
    calculated_list['FALSE'] = calculated_list[False]
    del calculated_list[False]

    print(f"Calculated words: {len(calculated_list)}")
    print(f"Total words: {len(word_list)}")

    minimum: int = 1000
    maximum: int = 0

    for word in word_list:
        if word not in calculated_list:
            raise Exception(f"Word {word} not calculated!")

    guesses_list: List[int] = [len(guesses) for word, guesses in calculated_list.items()]
    average = sum(guesses_list) / len(calculated_list)
    minimum: int = min(guesses_list)
    maximum: int = max(guesses_list)

    print(f"Minimum guesses: {minimum}")
    print(f"Maximum guesses: {maximum}")
    print(f"Average guesses: {average}")

    # Sort
    with open(GUESS_FILE, "w") as file:
        ordered_words = sorted(calculated_list.items(), key=lambda pair: pair[0])
        for word, guesses in ordered_words:
            file.write(f"{word}: {guesses}\n")
