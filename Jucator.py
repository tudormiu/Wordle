import copy
from multiprocessing.dummy.connection import Connection
from typing import List, Dict


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


def expected_value(candidat, numar_cuvinte):
    s = 0
    frecventa = [0] * 243

    import math

    for cuvant in lista_cuvinte:
        frecventa[pattern(candidat, cuvant)] += 1

    for ct in frecventa:
        if ct:
            s += ct / numar_cuvinte * math.log2(numar_cuvinte / ct)

    return s


def aproximare_guessuri_ramase(biti_incertitudine):
    '''Functia estimeaza pornind de la o presupunere initiala ca ar fi nevoie de aproximativ 3.75 incercari pentru a ghici
    cuvantul. Stiind ca avem, initial, 13.5 biti de incertitudine si ca, in momentul in care raman 0, ghicim din prima si
    cand avem un bit de incertitudine ghicim din 1,5 incercari, am calculat raportul dintre cele 2 valori si am presupus
    (stiind ca e eronat) ca distributia lor e liniara, aproximand o constanta de 5.2 ca fiind raportul dinte
    incertitudinea ramasa si numarul necesar de guessuri, peste ultimul guess, necesar'''

    guessuri_ramase = 1 + biti_incertitudine / 5.20
    return guessuri_ramase


def expected_score(numar_incercare, ev, incertitudine_ramasa, constanta, lungime_cuvinte):
    exp_score = numar_incercare * constanta / lungime_cuvinte + (1 - (constanta / lungime_cuvinte)) * (
                numar_incercare + aproximare_guessuri_ramase(incertitudine_ramasa - ev))
    return exp_score


def entropie_lista(lungime_lista_cuvinte):
    import math
    return math.log2(lungime_lista_cuvinte)


def play(cuvinte: List[str] = None, connection: Connection = None):
    # lungime = len(lista_cuvinte)
    # for cuv in lista_cuvinte:
    #    if expected_value(cuv, lungime) > max:
    #        max = expected_value(cuv, lungime)
    #        first_guess= cuv
    #    print(round(i/11454, 2)*100 , '%')
    #    i += 1
    # print (first_guess)
    # print (max)

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

    while ultimul_model != int(22222):
        numar_incercare += 1
        lungime_cuvinte = len(lista_cuvinte)

        for i in range(lungime_cuvinte - 1, -1, -1):
            if check(lista_cuvinte[i], ultimul_model, ultimul_guess) == 0:
                lista_cuvinte.pop(i)

        lungime_cuvinte = len(lista_cuvinte)

        max = 50
        entropie_ramasa = entropie_lista(lungime_cuvinte)

        for nou_candidat in lista_candidati:

            ev = expected_value(nou_candidat, lungime_cuvinte)
            ct_num = nou_candidat in lista_cuvinte

            '''if expected_value(nou_candidat, lungime_cuvinte) > max:
                            max = expected_value(nou_candidat, lungime_cuvinte)'''
            scor_asteptat = expected_score(numar_incercare, ev, entropie_ramasa, ct_num, lungime_cuvinte)
            if scor_asteptat < max and scor_asteptat != 0:
                max = scor_asteptat
                ultimul_guess = nou_candidat

        print(lista_cuvinte)
        print('')
        print(ultimul_guess, max)
        if connection:
            connection.send(ultimul_guess[0:5])
            ultimul_model = int(connection.recv())
        else:
            ultimul_model = int(input("Introduceti modelul obtinut prin utilizarea guessului de mai sus:"))

def calculate_second_word():

     lista_rezultate = []

     for current_model in lista_modele:

         cuvinte_temp = copy.deepcopy(lista_cuvinte)
         ultimul_model: int = current_model

         ultimul_guess = 'TAREI\n'

         for i in range(243):
             if check(lista_cuvinte[i], ultimul_model, ultimul_guess) == 0:
                 lista_cuvinte.pop(i)
         lungime_cuvinte = len(lista_cuvinte)
         max = 0

         for nou_candidat in lista_candidati:
             ev = expected_value(nou_candidat, lungime_cuvinte)
             ct_num = nou_candidat in lista_cuvinte

             if expected_value(nou_candidat, lungime_cuvinte) > max:
                 max = expected_value(nou_candidat, lungime_cuvinte)
                 ultimul_guess = nou_candidat

         lista_rezultate.append(ultimul_guess)
         print(current_model, ultimul_guess)

     print(lista_rezultate)

if __name__ == "__main__":
    with open("cuvinte_wordle.txt") as f_cuvinte:
        lista_cuvinte = list(f_cuvinte)

    lista_candidati = copy.deepcopy(lista_cuvinte)

    lista_modele = []
    lista_second_guesses = []

    with open("lista_modele.txt") as f_modele:
        for line in f_modele:
            lista_modele.append(int(line.rstrip()))

    with open("lista_second_guesses.txt") as lista_guesses:
        for line in lista_guesses:
            lista_second_guesses.append(line.rstrip())

    play()
    #calculate_second_word()
