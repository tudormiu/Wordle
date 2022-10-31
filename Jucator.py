def check(cuvant, model, candidat):
    poz = 4
    while model:
        ult = model % 10
        if (ult == 0 and candidat.find(cuvant[poz]) != -1) or \
                (ult == 1 and candidat.find(cuvant[poz], 0, poz) == -1 and candidat.find(cuvant[poz], poz + 1) == -1) or \
                (ult == 2 and cuvant[poz] != candidat[poz]):
            return 0
        model //= 10
        poz -= 1
    return 1


def expected_value(cuvant, numar_cuvinte):
    s = 0
    import math
    for model in lista_modele:
        ct = 0
        for candidat in lista_cuvinte:
            ct += check(cuvant, model, candidat)
        if ct:
            s += ct/numar_cuvinte * math.log2(numar_cuvinte/ct)
    return s


with open("cuvinte_wordle.txt") as f_cuvinte:
    lista_cuvinte = list(f_cuvinte)

lista_modele = []

with open("lista_modele.txt") as f_modele:
    for line in f_modele:
        lista_modele.append(int(line.rstrip()))

lungime = len(lista_cuvinte)

for cuv in lista_cuvinte:
    print(expected_value(cuv, lungime))
