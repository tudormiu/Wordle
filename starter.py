import time
from argparse import ArgumentParser, Namespace
from multiprocessing import Pipe, Process, Manager
from multiprocessing.pool import ThreadPool
from typing import List, Dict

from Joc import remote_start_app, remote_start_app_with_word
from Jucator import play

# Fisierul in care se salveaza solutiile
GUESS_FILE = "solutii2.yaml"


def calculate_words(words: List[str], start_index: int, dictionary: Dict[str, List[str]],
                    extra_arguments: Dict[str, any]):
    """ Calculeaza fiecare cuvant din n in n pasi, incepand cu start_index, si salveaza lista de guess-uri in dictionar.
    n este precizat in keyword-ul calculate_step. """

    # Cream un pipe (conexiune) si salvam cele doua capete ale conexiunii in connection1 and connection2
    connection1, connection2 = Pipe(duplex=True)

    # Cream un proces pentru functia care porneste interfata grafica, careia ii trimitem lista de cuvinte,
    # pozitia de start, un cap al conexiunii si marimea pasului (keyword-ul calculate_step prin extra_arguments).
    game_process = Process(target=remote_start_app_with_word, args=(words, start_index, connection1),
                           kwargs=extra_arguments)

    # Pornim interfata grafica prin acest proces, pentru a putea rula in paralel cu jucatorul.
    game_process.start()

    # Luam un range (lista de numere) care incepe de la prima pozitie, se duce pana la sfarsitul listei
    # si sare din n in n pasi (calculate_step), iar pentru fiecare numar luam cuvantul de pe acea pozitie.
    for index in range(start_index, len(words), extra_arguments['calculate_step']):
        word: str = words[index]

        # Cream un proces pentru jucator prin functia play, careia ii transmitem lista de cuvinte si
        # celalalt cap al conexiunii (si keyword-ul "log" fals pentru a nu afisa nimic in consola)
        player = Process(target=play, args=(words, connection2), kwargs={'log': False})
        player.start()

        # Asteptam ca jucatorul sa termine, adica sa gaseasca lista de guess-uri.
        player.join()

        # Stim ca atunci cand interfata primeste cuvantul corect de la jucator, aceasta trimite lista de guess-uri
        # prin conexiune, asa ca o citim prin capul conexiunii corespunzator jucatorului.
        guess_list: List[str] = connection2.recv()

        # Ne asiguram ca ultimul guess (cuvantul corect) este acelasi ca acela pe care l-am ales din lista
        # (Asta nu ar trebui sa se poata intampla, doar daca lista de cuvinte din functie se schimba cumva)
        if guess_list[len(guess_list) - 1] != word:
            raise Exception("Synchronization failed")

        # Setam lista de guess-uri corespunzatoare cuvantului in dictionar
        dictionary[word] = guess_list

        # Scriem in consola ce cuvant a fost calculat si de catre care thread.
        # (numerotarea incepe de la pozitia 0, dar noi numerotam thread-urile de la 1 asa ca adaugam 1)
        print(f"Thread #{start_index + 1}: Word {word} took {len(guess_list)} guesses {guess_list}!")

    # Asteptam ca interfata sa se inchida
    game_process.join()


if __name__ == "__main__":
    # Cream parser-ul de argumente
    parser: ArgumentParser = ArgumentParser(
        prog="Wordle",
        description="Wordle Game & Solver",
        epilog="Made by Deaconescu Mario, Miu Tudor, and Berbece David"
    )

    # Adaugam fiecare argument posibil al script-ului
    parser.add_argument("-a", "--all", action='store_true')
    parser.add_argument("-m", "--manual")
    parser.add_argument("-t", "--threads", default=1)
    parser.add_argument("-q", "--quit", action='store_true')

    # Parsam argumentele
    args: Namespace = parser.parse_args()

    # Citim lista de cuvinte din fisier
    word_list: List[str]
    with open("cuvinte_wordle.txt") as f_cuvinte:
        # Fiecare linie include caracterul newline ( '\n' ) pe care il scoatem prin a pastra doar primele 5 caractere
        word_list = [word[:5] for word in list(f_cuvinte)]

    # Numarul de thread-uri (cuvinte calculate in paralel) va fi luat din argumentul --threads (sau -t)
    number_of_threads: int = int(args.threads)

    # Daca avem parametrul --all e setat, atunci pasul cu care sarim cuvinte e egal cu numarul de thread-uri.
    # Astfel, thread-ul n va calcula pozitiile n, n + calculate_step, n + calculate_step * 2, ...
    # Daca nu, calculate_step va fi setat la 0 pentru a semnala interfetei ca vrem sa calculam un singur cuvant.
    arguments: Dict[str, int] = {'calculate_step': number_of_threads if args.all else 0}
    if args.all:
        # Daca vrem sa calculam toate cuvintele, atunci vrem ca interfata sa treaca automat la urmatorul cuvant,
        # iar daca nu mai are cuvinte de calculat, sa se inchida.
        arguments['auto_quit'] = True

        # Avem nevoie de variabila manager pentru a crea un dictionar care sa poata fi folosit de mai multe procese
        # in acelasi timp
        manager = Manager()

        # Prin manager, cream dictionarul
        word_dictionary: Dict[str, List[str]] = manager.dict()

        # Cream un ThreadPool (un fel de lista de thread-uri) care sa aloce toate cele number_of_threads procese
        with ThreadPool(processes=number_of_threads) as pool:
            # Pornim functia calculate_words pe fiecare thread, cu o lista de parametrii.
            # Fiecare element din lista de parametrii este un tuplu de 4 variabile, cele 4 variabile care vor fi
            # transmise functiei calculate_words pentru fiecare thread.
            result = pool.starmap_async(calculate_words, [(word_list, thread, word_dictionary, arguments) for thread in
                                                          range(number_of_threads)])
            seconds_elapsed = 1
            inactive_seconds = 0
            # Asteptam o secunda pentru a fi calculate primele cuvinte
            time.sleep(1)

            # Numarul de cuvinte ramase la ultima iteratie
            last_remaining_words: int = 0
            while not result.ready():  # Cat timp procese nu au terminat
                # Vedem cate cuvinte pe secunde calculam in medie
                words_per_second = len(word_dictionary) / seconds_elapsed

                # Calculam cate cuvinte avem ramase
                remaining_words = len(word_list) - len(word_dictionary)

                # Daca nu am mai calculat niciun cuvant intre timp, inseamna ca programul a fost inactiv ultima secunda
                if last_remaining_words == remaining_words:
                    inactive_seconds += 1
                else:
                    inactive_seconds = 0
                    last_remaining_words = remaining_words

                # Daca programul a fost inactiv 2 secunde, inchidem procesele.
                # Cel mai lung proces dureaza aproximativ o secunda, deci daca au trecut doua probabil programul
                # s-a terminat prematur
                if inactive_seconds == 2:
                    break

                # Daca avem 0 cuvinte pe secunda, nu putem calcula cate secunde avem ramase
                if words_per_second == 0:
                    seconds_left: int = 0
                else:
                    seconds_left: int = int(remaining_words // words_per_second)

                # Afisam in consola progresul
                print("=======================")
                print(
                    f"{(len(word_dictionary) / len(word_list) * 100):.2f}% complete! ({seconds_left} seconds remaining)")
                print("=======================")

                # Asteptam inca o secunda pana la urmatoarea iteratie
                seconds_elapsed += 1
                time.sleep(1)

            # Daca procesele s-au incheiat, putem inchide ThreadPool-ul
            pool.close()

        # Se poate intampla ca unele thread-uri sa se opreasca prematur (motiv nedeterminat), iar astfel lista de
        # cuvinte calculate nu va fi completa, asa ca verificam ce cuvinte nu au fost calculate, iar apoi le calculam
        # normal (fara thread-uri) pentru ca asa stim sigur ca nu esueaza.
        unprocessed_words: List[str] = []

        # Deoarece ii dam interfetei cuvintele manual, ii setam calculate_step 0.
        arguments['calculate_step'] = 0
        arguments['auto_quit'] = True

        for word in word_list:
            # Daca cuvantul nu se afla in dictionar, nu a fost calculat, deci il punem in lista cuvintelor necalculate.
            if word not in word_dictionary:
                unprocessed_words.append(word)

        for word in unprocessed_words:
            # Asemanator cu functia calculate_words, avem nevoie de un pipe pentru a permite comunicarea intre
            # joc si jucator
            connection1, connection2 = Pipe(duplex=True)

            # Deoarece functia remote_start_app_with_word primeste pozitia cuvantului si nu cuvantul insusi,
            # trebuie sa cautam ce pozitie are cuvantul mai intai.
            game = Process(target=remote_start_app_with_word,
                           args=(word_list, word_list.index(word), connection1), kwargs=arguments)

            player = Process(target=play, args=(word_list, connection2), kwargs={'log': False})

            game.start()
            player.start()

            # Jucatorul se va inchide inaintea jocului, deci pe el il asteptam primul
            player.join()
            game.join()

            # Asemanator cu functia calculate_words, preluam lista de guess-uri din conexiune.
            guess_list: List[str] = connection2.recv()

            # Setam lista de guess-uri corespunzatoare cuvantului in dictionar
            word_dictionary[word] = guess_list

            # Afisam progresul in consola
            print(f"Calculating remaining words: {(len(word_dictionary) / len(word_list) * 100):.2f}% complete!")

        # Acum ca am calculat toate cuvintele, le scriem in fisier
        with open(GUESS_FILE, "w") as file:
            # Deoarece thread-urile merg in paralel, cuvintele nu vor fi calculate in ordine, asa ca trebuie sa le
            # sortam alfabetic dupa cuvant.
            # (In word_dictionary.items() avem (cuvant, lista_guessuri), asa ca sortam dupa prima componenta (pair[0]),
            # adica dupa cuvant)
            ordered_words = sorted(word_dictionary.items(), key=lambda pair: pair[0])
            for word, guesses in ordered_words:
                # Scriem in fisier cuvantul, urmat de lista de cuvinte.
                # Folosim acest format (yaml) pentru a fi mai usor de citit de catre alt script python.
                # Daca foloseam direct o librarie yaml, aceasta ar fi afisat fiecare guess pe o linie noua, ceea ce ar
                # fi facut un fisier foarte mare.
                file.write(f"{word}: {guesses}\n")
    else:
        # Pe cazul in care calculam un singur cuvant, folosim o simpla conexiune si doua procese.
        connection1, connection2 = Pipe(duplex=True)
        if args.manual:
            # Inainte de a porni, ne asiguram ca avem cuvantul ales in lista de cuvinte
            if args.manual.upper not in word_list:
                raise Exception("Word not in list")

            # Daca avem argumentul --manual, transmitem interfetei pozitia cuvantului ales din lista de cuvinte
            game = Process(target=remote_start_app_with_word,
                           args=(word_list, word_list.index(args.manual.upper()), connection1), kwargs=arguments)
        else:
            # Daca nu, folosim functia remote_start_app, care isi alege automat (si aleator) un cuvant din lista
            game = Process(target=remote_start_app, args=(word_list, connection1), kwargs=arguments)

        # Asemanator cu mai sus, pornim pe rand cele doua procese si asteptam sa termine.
        player = Process(target=play, args=(word_list, connection2))
        game.start()
        player.start()
        game.join()
        player.join()

        # Asemanator cu mai sus, preluam din conexiune lista de guess-uri si doar o afisam.
        print(connection2.recv())
