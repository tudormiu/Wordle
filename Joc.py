import string
from typing import Dict

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.animation import Animation
import re
import random

from enum import Enum

Config.set('graphics', 'resizable', 0)

# Change background color
Window.clearcolor = (0.1, 0.1, 0.1, 1)
Window.size = (1000, 750)


class LetterState(Enum):
    EMPTY = -1
    INCORRECT = 0
    PARTIAL = 1
    CORRECT = 2


def get_model_from_word(word: str, right_word: str) -> str:
    # Create letter dict
    letter_frequencies: Dict[str, int] = {}
    for letter in string.ascii_uppercase:
        letter_frequencies[letter] = 0
    # Calculate letter dict
    for character in right_word:
        letter_frequencies[character] += 1
    # Create model
    model: str = ""
    for index in range(5):
        # Check if right letter
        if word[index] == right_word[index]:
            model += str(LetterState.CORRECT.value)
            letter_frequencies[word[index]] -= 1
        elif letter_frequencies[word[index]] > 0:
            model += str(LetterState.PARTIAL.value)
            letter_frequencies[word[index]] -= 1
        else:
            model += str(LetterState.INCORRECT.value)
    return model


class LetterBox(Button):

    guess_state = LetterState.EMPTY

    def __init__(self, **kwargs):
        super(LetterBox, self).__init__(**kwargs)

    def set_incorrect(self):
        if self.guess_state == LetterState.EMPTY:
            anim = Animation(background_color=(0.2, 0.2, 0.2, 1), duration=0.2)
            anim.start(self)
        else:
            self.background_color = (0.2, 0.2, 0.2, 1)
        self.guess_state = LetterState.INCORRECT

    def set_partial(self):
        if self.guess_state == LetterState.EMPTY:
            anim = Animation(background_color=(230 / 255, 188 / 255, 5 / 255, 255), duration=0.2)
            anim.start(self)
        else:
            self.background_color = (230 / 255, 188 / 255, 5 / 255, 255)
        self.guess_state = LetterState.PARTIAL

    def set_correct(self):
        if self.guess_state == LetterState.EMPTY:
            anim = Animation(background_color=(75 / 255, 156 / 255, 34 / 255, 255), duration=0.2)
            anim.start(self)
        else:
            self.background_color = (75 / 255, 156 / 255, 34 / 255, 255)
        self.guess_state = LetterState.CORRECT

    def set_empty(self):
        anim = Animation(background_color=(0, 0, 0, 0), duration=0.2)
        anim.start(self)
        self.guess_state = LetterState.EMPTY

    def update_box(self, new_letter: str, state):
        self.text = new_letter
        self.color = (1, 1, 1, 3)
        if state == LetterState.INCORRECT:
            self.set_incorrect()
        elif state == LetterState.PARTIAL:
            self.set_partial()
        elif state == LetterState.CORRECT:
            self.set_correct()
        else:
            self.set_empty()




class GuessLine(BoxLayout):
    letters = list()

    def __init__(self, **kwargs):
        super(GuessLine, self).__init__(**kwargs)
        self.letters = list()
        for i in range(5):
            letter_box = LetterBox()
            self.add_widget(letter_box)
            self.letters.append(letter_box)


class GuessList(AnchorLayout):
    guess_list = list()
    current_guess = 0
    correct_word: str

    def __init__(self, word_list, word: str, **kwargs):
        super(GuessList, self).__init__(**kwargs)
        self.word_list = [word[0:5] for word in word_list]
        self.box_layout = BoxLayout(orientation='vertical', size=(520, 730), size_hint=(None, None), spacing=5)
        self.box_layout.add_widget(InputBox())
        for i in range(6):
            guess = GuessLine()
            self.guess_list.append(guess)
            self.box_layout.add_widget(guess)
        self.add_widget(self.box_layout)
        self.correct_word = word

    def add_line(self):
        guess = GuessLine()
        self.guess_list.append(guess)
        self.box_layout.add_widget(guess)

    def process_model(self, model: str):
        if model == "22222":
            win_label = Label(font_size=50, size=(520, 730), size_hint=(None, None), color=(0, 0, 0, 0), text=f"GUESSES: {self.current_guess}")
            self.box_layout.add_widget(win_label)
            Animation(color=(1, 1, 1, 1)).start(win_label)



class InputBox(BoxLayout):

    def on_submit(self, text_input: TextInput):
        text = text_input.text
        guess_widget: GuessList = self.parent.parent
        if len(text) < 5 or text_input.text not in guess_widget.word_list:
            # Start incorrect guess animation and exit
            anim = Animation(background_color=(0.6, 0, 0, 1), duration=0.1) + Animation(background_color=(0.1, 0.1, 0.1, 1), duration=0.1)
            anim.start(text_input)
            return
        # If the current guess is greater than 5, just return the last line
        guess: GuessLine = guess_widget.guess_list[min(5, guess_widget.current_guess)]
        model = get_model_from_word(text, guess_widget.correct_word)
        for i in range(5):
            current_letter = guess.letters[i]
            current_letter.update_box(text[i], LetterState(int(model[i])))
        guess_widget.current_guess += 1
        if guess_widget.current_guess >= 6 and model != "22222":
            # If we used all guesses, move all of them up by 1 line to make space for the new guess
            for line in range(1, 6):
                original_guess: GuessLine = guess_widget.guess_list[line]
                new_guess: GuessLine = guess_widget.guess_list[line - 1]
                for i in range(5):
                    original_letter = original_guess.letters[i]
                    new_guess.letters[i].update_box(original_letter.text, original_letter.guess_state)
            # Clear the last line for the next guess
            for i in range(5):
                guess_widget.guess_list[5].letters[i].update_box("", LetterState.EMPTY)
        text_input.text = ""
        if model == "22222":
            self.parent.remove_widget(self)
        guess_widget.process_model(model)



class WordleApp(App):

    def __init__(self, word_list, word: str, **kwargs):
        super(WordleApp, self).__init__(**kwargs)
        self.word_list = word_list
        self.word = word

    def build(self):
        return GuessList(self.word_list, self.word)


if __name__ == "__main__":
    with open("cuvinte_wordle.txt") as f_cuvinte:
        word_list = list(f_cuvinte)
    app = WordleApp(word_list, word_list[random.randint(0, len(word_list))][0:5])
    app.run()
