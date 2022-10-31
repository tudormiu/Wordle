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
Window.size = (1500, 1000)


class LetterState(Enum):
    EMPTY = -1,
    INCORRECT = 0,
    PARTIAL = 1,
    CORRECT = 2


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
        self.box_layout = BoxLayout(orientation='vertical', size=(1040, 1460), size_hint=(None, None), spacing=10)
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
            win_label = Label(font_size=100, size=(1040, 200), size_hint=(None, None), color=(0, 0, 0, 0), text=f"GUESSES: {self.current_guess}")
            self.box_layout.add_widget(win_label)
            Animation(color=(1, 1, 1, 1)).start(win_label)



class InputBox(BoxLayout):

    def on_submit(self, text_input: TextInput):
        text = text_input.text
        guess_widget: GuessList = self.parent.parent
        if len(text) < 5 or text_input.text not in guess_widget.word_list:
            anim = Animation(background_color=(0.6, 0, 0, 1), duration=0.1) + Animation(background_color=(0.1, 0.1, 0.1, 1), duration=0.1)
            anim.start(text_input)
            return
        guess: GuessLine = guess_widget.guess_list[min(5, guess_widget.current_guess)]
        return_model = ""
        for i in range(5):
            current_letter = guess.letters[i]
            current_letter.color = (1, 1, 1, 3)
            state = LetterState.EMPTY
            # Check if correct letter
            if text[i] == guess_widget.correct_word[i]:
                state = LetterState.CORRECT
                return_model += "2"
            # Check if incorrect letter
            elif guess_widget.correct_word.find(text[i]) == -1:
                state = LetterState.INCORRECT
                return_model += "0"
            else:
                return_model += "1"
                state = LetterState.PARTIAL
            current_letter.update_box(text[i], state)
        guess_widget.current_guess += 1
        if guess_widget.current_guess >= 6 and return_model != "22222":
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
        if return_model == "22222":
            self.parent.remove_widget(self)
        guess_widget.process_model(return_model)



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
