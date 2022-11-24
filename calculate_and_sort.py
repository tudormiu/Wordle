import copy
from collections import OrderedDict
from typing import Dict, List
import yaml

def pattern(cuvant, candidat):
    pat = 0
    putere = 1

    for poz in [4, 3, 2, 1, 0]:
        if candidat[poz] == cuvant[poz]:
            pat += putere * 2
        if candidat[poz] != cuvant[poz] and (
                cuvant.find(candidat[poz]) != -1 or cuvant.find(candidat[poz], poz + 1, 5) != -1):
            pat += putere
        putere *= 3

    return pat

def check(cuvant, model, candidat):
    poz = 4

    for i in range(5):
        ult = model % 10
        if (ult == 0 and cuvant.find(candidat[poz]) != -1) or \
                (ult == 1 and cuvant.find(candidat[poz], 0, poz) == -1 and cuvant.find(candidat[poz], poz + 1) == -1) or \
                (ult == 1 and cuvant[poz] == candidat[poz]) or \
                (ult == 2 and cuvant[poz] != candidat[poz]):
            return 0
        model //= 10
        poz -= 1
    return 1

GUESS_FILE = "solutii_algoritm_2.yaml"

with open("cuvinte_wordle.txt") as f_cuvinte:
    lista_originala_cuvinte = list(f_cuvinte)

with open(GUESS_FILE, "r") as file:
    calculated_list: Dict[str, List[str]] = yaml.safe_load(file)
with open("cuvinte_wordle.txt") as f_cuvinte:
    word_list = [word[:5] for word in list(f_cuvinte)]

print(f"Total words: {len(calculated_list)}")

guesses_list: List[int] = [len(guesses) for word, guesses in calculated_list.items()]
average = sum(guesses_list) / len(calculated_list)
minimum: int = min(guesses_list)
maximum: int = max(guesses_list)

lista_cuvinte = [word for word in calculated_list]
lista_cuvinte_copy = []
import copy
lista_cuvinte_copy = copy.deepcopy(lista_originala_cuvinte)

for cuvant in lista_cuvinte:
    lungime_cuvinte = len(lista_originala_cuvinte)
    ultimul_guess = 'TAREI\n'
    ultimul_model = pattern(cuvant , 'TAREI\n')

    for i in range(lungime_cuvinte - 1, -1, -1):
        if pattern(lista_cuvinte_copy[i], ultimul_guess) != ultimul_model:
            lista_cuvinte_copy.pop(i)

    lungime_cuvinte = len(lista_cuvinte_copy)
    ultimul_guess = calculated_list[cuvant][1]
    ultimul_model = pattern(cuvant , ultimul_guess)

    for i in range(lungime_cuvinte - 1, -1, -1):
        if pattern(lista_cuvinte_copy[i], ultimul_guess) != ultimul_model:
            lista_cuvinte_copy.pop(i)

    import math
    print(math.log2(len(lista_cuvinte_copy)), end=' ')
    lista_cuvinte_copy = copy.deepcopy(lista_originala_cuvinte)

print('\n')
j=0
for cuvant in lista_cuvinte:
    print(guesses_list[j] - 2, end=' ')
    j+=1

print('\nLista cuvinte selectate:',lista_cuvinte, '\n')

print(f"Minimum guesses: {minimum}")
print(f"Maximum guesses: {maximum}")
print(f"Average guesses: {average}")

# Sort
with open(GUESS_FILE, "w") as file:
    ordered_words = sorted(calculated_list.items(), key=lambda pair: pair[0])
    for word, guesses in ordered_words:
        file.write(f"{word}: {guesses}\n")
