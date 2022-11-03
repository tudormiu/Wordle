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
    frecventa= [0]*243

    import math

    for cuvant in lista_cuvinte:
        frecventa[pattern(candidat, cuvant)] += 1

    for ct in frecventa:
        if ct:
            s += ct / numar_cuvinte * math.log2(numar_cuvinte / ct)

    return s


def aproximare_guessuri_ramase(biti_incertitudine):
    #Functia estimeaza pornind de la o presupunere initiala ca ar fi nevoie de aproximativ 3.75 incercari pentru a ghici
    #cuvantul. Stiind ca avem, initial, 13.5 biti de incertitudine si ca, in momentul in care raman 0, ghicim din prima si
    #cand avem un bit de incertitudine ghicim din 1,5 incercari, am calculat raportul dintre cele 2 valori si am presupus
    # (stiind ca e eronat) ca distributia lor e liniara, aproximand o constanta de 5.2 ca fiind raportul dinte
    #incertitudinea ramasa si numarul necesar de guessuri, peste ultimul guess, necesar

    guessuri_ramase = 1 +  biti_incertitudine/5.20
    return guessuri_ramase


def expected_score(numar_incercare, ev, incertitudine_ramasa, constanta):
    exp_score = numar_incercare * ev * constanta + (1 - ev)*(numar_incercare + aproximare_guessuri_ramase(incertitudine_ramasa-ev))
    return exp_score

def entropie_lista(lungime_lista_cuvinte):
    import math
    return math.log2(lungime_lista_cuvinte)


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
    numar_incercare = 1

    while ultimul_model != int(22222):
        numar_incercare += 1
        lungime_cuvinte = len(lista_cuvinte)

        for i in range(lungime_cuvinte - 1, -1, -1):
            if check(lista_cuvinte[i], ultimul_model, ultimul_guess) == 0:
                junk = lista_cuvinte.pop(i)

        lungime_cuvinte = len(lista_cuvinte)

        max = 0
        entropie_ramasa = entropie_lista(lungime_cuvinte)

        for nou_candidat in lista_candidati:
            ev = expected_value(nou_candidat, lungime_cuvinte)
            ct_num = nou_candidat in lista_cuvinte

            if expected_score(numar_incercare, ev, entropie_ramasa, ct_num) > max:
                max = expected_score(numar_incercare, ev, entropie_ramasa, ct_num)
                ultimul_guess = nou_candidat

        print(ultimul_guess)
        ultimul_model = int(input("Introduceti modelul obtinut prin utilizarea guessului de mai sus:"))



with open("cuvinte_wordle.txt") as f_cuvinte:
    lista_cuvinte = list(f_cuvinte)

import copy
lista_candidati = copy.deepcopy(lista_cuvinte)

lista_modele = []

with open("lista_modele.txt") as f_modele:
    for line in f_modele:
        lista_modele.append(int(line.rstrip()))

play()
