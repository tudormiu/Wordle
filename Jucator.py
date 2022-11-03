import copy
def base3base10(intrare):
    pow = 1
    rez = 0
    while intrare:
        rez += (intrare % 10) * pow
        pow *= 3
        intrare //= 10
    return rez

def check(cuvant, model, candidat):
    poz = 4
    for i in range (5):
        ult = model % 10
        if (ult == 0 and candidat.find(cuvant[poz]) != -1) or \
                (ult == 1 and candidat.find(cuvant[poz], 0, poz) == -1 and candidat.find(cuvant[poz], poz + 1) == -1) or \
                (ult == 2 and cuvant[poz] != candidat[poz]):
            return 0
        model //= 10
        poz -= 1
    return 1

def pattern(candidat, cuvant):
    pat = 0
    pow = 1
    for poz in [4,3,2,1,0]:
        if candidat[poz] == cuvant[poz]:
            pat += pow * 2
        if candidat[poz] != cuvant[poz] and (cuvant.find(candidat[poz]) != -1 or cuvant.find(candidat[poz], poz + 1, 5) != -1):
            pat += pow
        pow *=3
    return pat


def expected_value(candidat, numar_cuvinte):
    s = 0
    import math
    frecventa= [0]*243
    for cuvant in lista_cuvinte:
        frecventa[pattern(candidat, cuvant)] += 1
    for ct in frecventa:
        if ct:
            s += ct / numar_cuvinte * math.log2(numar_cuvinte / ct)
    return s


def play():
    lungime = len(lista_cuvinte)

    max = 0
    i = 1

    # for cuv in lista_cuvinte:
    #    if expected_value(cuv, lungime) > max:
    #        max = expected_value(cuv, lungime)
    #        first_guess= cuv
    #    print(round(i/11454, 2)*100 , '%')
    #    i += 1
    # print (first_guess)
    # print (max)

    ultimul_model = int(input("Introduceti modelul obtinut prin utilizarea guessului 'TAREI':"))
    ultimul_guess = 'TAREI\n'

    while ultimul_model != int(22222):
        lungime_cuvinte = len(lista_cuvinte)
        for i in range(lungime_cuvinte - 1, 0, -1):
            if check(lista_cuvinte[i], ultimul_model, ultimul_guess) == 0:
                junk = lista_cuvinte.pop(i)
        max = 0
        for nou_candidat in lista_candidati:
            if expected_value(nou_candidat, lungime_cuvinte) > max:
                max = expected_value(nou_candidat, lungime_cuvinte)
                ultimul_guess = nou_candidat
        print(ultimul_guess)
        ultimul_model = int(input("Introduceti modelul obtinut prin utilizarea guessului de mai sus:"))



with open("cuvinte_wordle.txt") as f_cuvinte:
    lista_cuvinte = list(f_cuvinte)
from copy import deepcopy
lista_candidati = copy.deepcopy(lista_cuvinte)

lista_modele = []

with open("lista_modele.txt") as f_modele:
    for line in f_modele:
        lista_modele.append(int(line.rstrip()))

play()