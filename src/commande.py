Prototype = True


import os
import ctypes


def cls():
    if os.name == "nt":
        os.system("cls")
    elif os.name == "posix":
        os.system("clear")

def title(name):
    if os.name == "nt":
        ctypes.windll.kernel32.SetConsoleTitleW(name)
    elif os.name == "posix":
        os.system(f'echo -e "\033]0;{name}\007"')

def clear():
    if os.name == "nt":
        os.system("cls")
    elif os.name == "posix":
        os.system("clear")