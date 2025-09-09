Prototype = True
Prototype_INFO = "Tous refaire, ne pas charger tous le fichier ( lecture par ligne I/O) a faire. et pour quoi il ne complete plus; surement des version"

from prompt_toolkit import PromptSession 
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from .color import *
import os
import time

def input_():
    global ligne_history, ligne_total_history, tableau_history
    ligne_history = 0
    ligne_total_history = 0
    tableau_history = []
    if os.path.exists('.history_SHELL'):
        with open(".history_SHELL", "r", encoding="utf-8") as fichier:
            for ligne in fichier:
                tableau_history.append(ligne.strip())
                ligne_total_history += 1
    ligne_total_history -= 1
    
    if os.path.isdir("Completist\\commande.txt"):
        with open("Completist\\commande.txt", "r", encoding="utf-8") as fichier:
            COMMANDS = [ligne.strip() for ligne in fichier if ligne.strip() and not ligne.startswith("#")]
    else:
        COMMANDS = []
    
    if os.path.isdir("Completist\\module.txt"):
        with open("Completist\\module.txt", "r", encoding="utf-8") as fichier:
            COMMANDS_module = [ligne.strip() for ligne in fichier if ligne.strip() and not ligne.startswith("#")]
    else:
        COMMANDS_module = []
    
    command_completer = WordCompleter(COMMANDS, ignore_case=True, match_middle=False)
    session = PromptSession(completer=command_completer)
    bindings = KeyBindings()
    
    global enter_pressed_once, return_stat
    enter_pressed_once = False
    return_stat = [False, None]
    
    def ajouter_lettre(buffer, lettre):
        global enter_pressed_once
        buffer.insert_text(lettre)
        enter_pressed_once = True
    
    for lettre in " ":
        @bindings.add(lettre)
        def _(event, lettre=lettre):
            ajouter_lettre(event.app.current_buffer, lettre)
            cmd = event.app.current_buffer.text
            cmd = cmd.replace("True", f"{VERT}True{RESET}")
            cmd = cmd.replace("False", f"{ROUGE[0]}False{RESET}")
            print(f"\033[4G\033[0K{cmd}", end='', flush=True)
            #print(f"\033[2K{VERT}└─{BLEU[0]}${RESET}{cmd}", end='', flush=True)
    
    @bindings.add("enter")
    def _(event):
        global enter_pressed_once, return_stat
        
        if event.app.current_buffer.text.strip():
            with open(".history_SHELL", "a") as fichier:
                fichier.write(event.app.current_buffer.text + '\n')
        
        if not enter_pressed_once:  # Si l'espace n'a pas été ajouté, n'attends pas l'espace
            cmd = event.app.current_buffer.text
            cmd = cmd.replace("True", f"{VERT}True{RESET}")
            cmd = cmd.replace("False", f"{ROUGE[0]}False{RESET}")
            #print(f"{VERT}└─{BLEU[0]}${RESET}{cmd}\033[1A")
            print(f"\033[4G\033[0K{cmd}\033[1A")
            return_stat[0] = True
            return_stat[1] = cmd
            event.app.exit()
        else:  # Si l'espace a été ajouté, continue normalement
            cmd = event.app.current_buffer.text
            cmd = cmd.replace("True", f"{VERT}True{RESET}")
            cmd = cmd.replace("False", f"{ROUGE[0]}False{RESET}")
            print(f"\033[4G\033[0K{cmd}\033[1A")
            #print(f"{VERT}└─{BLEU[0]}${RESET}{cmd}\033[1A")
            return_stat[0] = True
            return_stat[1] = event.app.current_buffer.text
            enter_pressed_once = False
            event.app.exit()
    
    # @bindings.add('c-c')
    # def _(event):
    #     print(ROUGE[0] + "Ctrl + C" + RESET)
    #     return_stat[0] = True
    #     return_stat[1] = "Ctrl + C"
    #     event.app.exit()
    
    @bindings.add('up')
    def _(event):
        global ligne_history, ligne_total_history, tableau_history
        if not ligne_history == ligne_total_history:
            ligne_history += 1
        #print(tableau_history[ligne_history])
        event.app.current_buffer.text = tableau_history[ligne_history]
    
    @bindings.add('down')
    def _(event):
        global ligne_history, ligne_total_history, tableau_history
        if not ligne_history == 0:
            ligne_history -= 1
        #print(tableau_history[ligne_history])
        event.app.current_buffer.text = tableau_history[ligne_history]
    
    while True:
        cmd = session.prompt("   ", key_bindings=bindings)
        if return_stat[0]:
            return return_stat[1]