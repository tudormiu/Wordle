#                                                           -Wordle Cracker-
<p><img align="center" src="https://github.com/tudormiu/Wordle/blob/26cf51baf4c94ecdf8beb8b28dcafb77f1977609/ezgif.com-gif-maker.gif" width="900" height="600" /></p>
sursa video -> https://www.youtube.com/watch?v=dQw4w9WgXcQ.

Proiect realizat de: 

    - Deaconescu Mario, grupa 151
    - Miu Tudor, grupa 151
    - Berbece David, grupa 151

$$\sqrt{2}$$

## Statistici si Notatii

   - Numărul mediu de încercări pentru ghicirea tuturor cuvintelor pe care l-am obtinut este: 3.9889121704208135
   - Codificarea pentru cuvintele incercate este:
        - 2, daca litera apare in cuvant, pe pozitia potrivita. (casuta este verde)
        - 1, daca litera apare in cuvant, dar pe alta pozitie. (casuta este portocalie)
        - 0, daca litara nu se gaseste in cuvant. (casuta este neagra)
## Instalare 

 - Pull din GitHub
 - In consola se executa comanda: ```pip3 install -r requirements.txt```
 - Pentru a juca manual: ```python3 joc.py```
 - Pentru a testa jucatorul: ```python3 jucator.py```
 - pentru a juca jucatorul cu jocul: ```python3 starter.py```

## Jucator 

   - Codificarea este formata doar cu cifrele 0,1 si 2. Asadar, modelele sunt numere scrise in baza 3. In program, aceste numere sunt transformate in baza 10, in scopul crearii unui vector de frecventa.
   - Pentru determinarea guess-ului cu cea mai mare entropie, vom folosi 3 liste:
      - lista cu cele 11454 de cuvinte, care nu se modifica pe parcursul rularii
      - lista cu toate numerele de 3 cifre scrise in baza 3
      - lista de cuvinte care se actualizeaza mereu in functie de modelul furnizat de joc
   - Algoritmul parcurge, pe rand, toate cuvintele din lista cea mare (presupunem ca cuvantul "i" este guess-ul cautat). Apoi, pentru fiecare cuvand se parcurge lista de modele(modelul "j"), iar pentru fiecare model se parcurge lista de cuvinte ramase. Astfel, se numara de cate ori cuvantul "i" poate avea modelul "j" in lista de cuvinte care se actualizeaza dinamic. Cu aceste informatii, putem calcula entropia pentru fiecare cuvant din lista cea mare, iar cuvantul cu entropia maxima va fi guess-ul ales.
   - Primul guess pe care l-am obtinut este "TAREI" cu entropie 6.413805505806506
   - Pentru eficinta din punct de vedere al timpului de executare, in fisierul ```lista_second_guesses.txt```, am precalculat si al doilea guess in functie de orice model obtinut in urma introducerii cuvantului "TAREI". 

## Joc 
     
   - Crearea jocului sta la baza mai multor clase in care sunt definite functiile necesare pentru colorarea casutelor, crearea liniilor, initializare, restartare, etc... Acestea sunt:
     -  ```class WordleApp(App)```
     -  ```class InputBox(BoxLayout)```
     -  ```class GuessList(AnchorLayout)```
     -  ```class GuessLine(BoxLayout)```
     -  ```class LetterBox(Button)```
     -  ```class LetterState(Enum)```
   - Prima data se construiesc 2 chenare, unul mare si cel in care se scrie, de la tastatura, input-ul. Mai apoi, in chenarul mare, se creaza 6 linii, iar in fiecare linie se construiesc 5 casute, pentru cele 5 litere.

## Comunicare si Crearea Fisierului cu Solutii

   - Aceasta este implementata in fisierul '''starter.py''' si se realizeaza cu ajutorul unui Pipe importat din modulul multiprocessing.
   - Comanda ```connection1, connection2 = Pipe(duplex=True)``` creeaza cele 2 conexiuni de care avem nevoie pentru a realiza comunicarea intre *Joc* si *Jucator*
   - Jocul isi alege fiecare cuvant din lista. Se creaza 2 procese, unul pentru *Joc*, iar celalalt pentru *Jucator*. Cand jucatorul termina, prin conexiunea ```connection2``` se preiau cuvintele incercate de acesta si se scriu in fisierul ```solutii2.yaml```.
   - Pentru folosirea eficienta a programurul se va folosi un parser de argumente. Argumentele sunt: 
       -  ```--threads [numar de thread-uri]``` care contine numarul de thread-uri.
       - ```--all``` care daca este setat, atunci vom calcula toate cuvintele din lista.
       - ```--manual [cuvant]``` care daca este setat, atunci se alege, manual, un singur cuvant din lista.
   - De asemenea, pentru a calcula toate cuvintele, vom folosi si un ThreadPool care sa aloce in mod eficient procesele numarului de thread-uri. Functia care calculeaza cuvintele va fi pornita pe fiecare thread, alaturi de o lista cu parametrii.
   
