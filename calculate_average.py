from typing import Dict

import yaml

GUESS_FILE = "guesses.yaml"

if __name__ == "__main__":
    with open(GUESS_FILE, "r") as file:
        word_list: Dict[str, int] = yaml.safe_load(file)
    average = sum([guesses for word, guesses in word_list.items()]) / len(word_list)
    print(average)
