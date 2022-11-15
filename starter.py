from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import List

from Joc import remote_start_app
from Jucator import play


if __name__ == "__main__":
    connection1, connection2 = Pipe(duplex=True)
    word_list: List[str]
    with open("cuvinte_wordle.txt") as f_cuvinte:
        word_list = list(f_cuvinte)
    game = Process(target=remote_start_app, args=(word_list, connection1))
    player = Process(target=play, args=(word_list, connection2))
    game.start()
    player.start()
    game.join()
    player.join()
