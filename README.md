#  -Wordle Cracker-
Proiect realizat de: 

    - Deaconescu Mario, grupa 151
    - Miu Tudor, grupa 151
    - Berbece David, grupa 151

## Statistici 

   Numărul mediu de încercări pentru ghicirea tuturor cuvintelor pe care l-am obtinut este:
    
## Instalare 

 - Pull din GitHub
 - In consola se executa comanda: ```pip3 install -r requirements.txt```
 - Pentru a juca manual: ```python3 joc.py```
 - Pentru a testa jucatorul: ```python3 jucator.py```
 - pentru a juca jucatorul cu jocul: ```python3 starter.py```

## Jucator 
    
   - Primul Guess:
            dcsvcs
   -  
    
    

## Joc 

la fel ca mai sus

## Comunicare si Crearea Fisierului cu Solutii

   - Aceasta este implementata in fisierul '''starter.py''' si se realizeaza cu ajutorul unui Pipe importat din modulul multiprocessing.
   - Comanda ```connection1, connection2 = Pipe(duplex=True)``` creeaza cele 2 conexiuni de care avem nevoie pentru a realiza comunicarea intre *Joc* si *Jucator*
   - Jocul isi alege fiecare cuvant din lista. Se creaza 2 procese, unul pentru *Joc*, iar celalalt pentru *Jucator*. Cand jucatorul termina, prin conexiunea ```connection2``` se preiau cuvintele incercate de acesta si se scriu in fisierul ```solutii2.yaml```.
   
   
   
   
   
   
   
   
   
   
   
   
   
   
    
