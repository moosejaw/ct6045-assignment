'''
To clarify: this code was originally used in
https://github.com/moosejaw/hiragana-game/blob/master/game.py
which is code I wrote myself.
'''
import colorama

class Color:
    """Class containing some common methods used for colorama."""
    def __init__(self):
        colorama.init()

    def reset(self):
        print(colorama.Style.RESET_ALL)

    def setRedText(self):
        print(colorama.Fore.RED)

    def setGreenText(self):
        print(colorama.Fore.GREEN)

    def setBlueText(self):
        print(colorama.Fore.BLUE)
