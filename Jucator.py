import copy
from multiprocessing.dummy.connection import Connection
from typing import List

ruleaza_algoritmul_1 = 0
ruleaza_algoritmul_2 = 0
ruleaza_algoritmul_3 = 1

def base3base10(intrare):
    put = 1
    rez = 0

    while intrare:
        rez += (intrare % 10) * put
        put *= 3
        intrare //= 10

    return rez


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


def pattern(candidat, cuvant):
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


def expected_value(candidat, numar_cuvinte, lista_cuvinte_ev):
    s = 0
    frecventa = [0] * 243

    import math

    for cuvant in lista_cuvinte_ev:
        frecventa[pattern(candidat, cuvant)] += 1

    for ct in frecventa:
        if ct:
            s += ct / numar_cuvinte * math.log2(numar_cuvinte / ct)

    return s


def aproximare_guessuri_ramase(biti_incertitudine):
    guessuri_ramase = 0
    putere = 1
    coeficienti = [1 , 0.7509383846 , -0.1381286976 , -0.0227391170 , 0.0127673413 , -0.0012171694]
    for i in coeficienti:
        guessuri_ramase += i * putere
        putere *= biti_incertitudine
    return guessuri_ramase


def expected_score(numar_incercare, ev, incertitudine_ramasa, constanta, lungime_cuvinte):
    exp_score = numar_incercare * constanta / lungime_cuvinte + (1 - (constanta / lungime_cuvinte)) * (
                numar_incercare + aproximare_guessuri_ramase(incertitudine_ramasa - ev))
    return exp_score


def entropie_lista(lungime_lista_cuvinte):
    import math
    return math.log2(lungime_lista_cuvinte)


def play(cuvinte: List[str] = None, connection: Connection = None, log: bool = True):

    if cuvinte:
        global lista_cuvinte
        lista_cuvinte = cuvinte
        global lista_candidati
        lista_candidati = copy.deepcopy(lista_cuvinte)

        global lista_modele
        lista_modele = []

        with open("lista_modele.txt") as f_modele:
            for line in f_modele:
                lista_modele.append(int(line.rstrip()))

    ultimul_model: int

    if connection:
        connection.send('TAREI')
        ultimul_model = int(connection.recv())
    else:
        ultimul_model = int(input("Introduceti modelul obtinut prin utilizarea guessului 'TAREI':"))

    ultimul_guess = 'TAREI\n'
    numar_incercare = 1

    if ultimul_model != int(22222):
        lungime_cuvinte = len(lista_cuvinte)
        for i in range(lungime_cuvinte - 1, -1, -1):
            if check(lista_cuvinte[i], ultimul_model, ultimul_guess) == 0:
                lista_cuvinte.pop(i)

        lista_second_guesses = []
        with open("lista_second_guesses_2.txt") as lista_guesses:
            for line in lista_guesses:
                lista_second_guesses.append(line.rstrip())

        if log:
            print(ultimul_model)

        pozitie_in_lista = base3base10(ultimul_model)
        ultimul_guess = lista_second_guesses[pozitie_in_lista]

        if log:
            print(lista_cuvinte)
            print('')
            print(ultimul_guess)
        if connection:
            connection.send(ultimul_guess[0:5])
            ultimul_model = int(connection.recv())
        else:
            ultimul_model = int(input("Introduceti modelul obtinut prin utilizarea guessului de mai sus:"))

    while ultimul_model != int(22222):
        numar_incercare += 1
        lungime_cuvinte = len(lista_cuvinte)

        for i in range(lungime_cuvinte - 1, -1, -1):
            if check(lista_cuvinte[i], ultimul_model, ultimul_guess) == 0:
                lista_cuvinte.pop(i)

        lungime_cuvinte = len(lista_cuvinte)

        if ruleaza_algoritmul_3:
            max = 50
            entropie_ramasa = entropie_lista(lungime_cuvinte)

        if ruleaza_algoritmul_1 or ruleaza_algoritmul_2:
            max = 0
        for nou_candidat in lista_candidati:
            ev = expected_value(nou_candidat, lungime_cuvinte, lista_cuvinte)

            if ruleaza_algoritmul_2 or ruleaza_algoritmul_1:
                if ruleaza_algoritmul_2:
                    if lungime_cuvinte:
                        if nou_candidat in lista_cuvinte:
                            ev += (1 / lungime_cuvinte)

                if ev > max:
                    max = ev
                    ultimul_guess = nou_candidat
                elif ev == max and nou_candidat in lista_cuvinte:
                    ultimul_guess = nou_candidat

            if ruleaza_algoritmul_3:
                ct_num = nou_candidat in lista_cuvinte
                scor_asteptat = expected_score(numar_incercare, ev, entropie_ramasa, ct_num, lungime_cuvinte)
                if scor_asteptat < max and scor_asteptat != 0:
                    max = scor_asteptat
                    ultimul_guess = nou_candidat

        if log:
            print(lista_cuvinte)
            print('')
            print(ultimul_guess, max)
        if connection:
            connection.send(ultimul_guess[0:5])
            ultimul_model = int(connection.recv())
        else:
            ultimul_model = int(input("Introduceti modelul obtinut prin utilizarea guessului de mai sus:"))


def calculate_first_word():
    i = 0
    max = 0
    lungime = len(lista_cuvinte)
    for cuv in lista_cuvinte:
        if expected_value(cuv, lungime, lista_cuvinte) > max:
            max = expected_value(cuv, lungime, lista_cuvinte)
            first_guess = cuv
        print(round(i / 11454, 2) * 100, '%')
        i += 1
    print(first_guess)
    print(max)

def calculate_second_word():
    lista_rezultate = []
    with open("cuvinte_wordle.txt") as f_cuvinte:
        lista_candidati = list(f_cuvinte)
    for current_model in lista_modele:

        lista_cuvinte_second_guess = copy.deepcopy(lista_candidati)
        ultimul_guess = 'TAREI\n'
        lungime_cuvinte = len(lista_cuvinte_second_guess)

        for i in range(lungime_cuvinte - 1, -1, -1):
            if check(lista_cuvinte_second_guess[i], current_model, ultimul_guess) == 0:
                lista_cuvinte_second_guess.pop(i)
        lungime_cuvinte = len(lista_cuvinte_second_guess)
        print(current_model, 'done', lungime_cuvinte)
        max = 0

        print (lista_cuvinte_second_guess)

        for nou_candidat in lista_candidati:
            ev = expected_value(nou_candidat, lungime_cuvinte, lista_cuvinte_second_guess)

            if ruleaza_algoritmul_2:
                if lungime_cuvinte:
                    if nou_candidat in lista_cuvinte:
                        ev += (1 / lungime_cuvinte)

            if ev > max:
                max = ev
                ultimul_guess = nou_candidat
            elif ev == max and nou_candidat in lista_cuvinte_second_guess:
                ultimul_guess = nou_candidat


        lista_rezultate.append(ultimul_guess)
        print(current_model, ultimul_guess)

    lista_second_guesses = open("lista_second_guesses_2.txt", "a")
    for i in range (243):
        lista_second_guesses.write(lista_rezultate[i])
    lista_second_guesses.close()

if __name__ == "__main__":
    with open("cuvinte_wordle.txt") as f_cuvinte:
        lista_cuvinte = list(f_cuvinte)

    lista_candidati = copy.deepcopy(lista_cuvinte)

    lista_modele = []


    with open("lista_modele.txt") as f_modele:
        for line in f_modele:
            lista_modele.append(int(line.rstrip()))

    play()
    #calculate_second_word()
    #calculate_first_word()
