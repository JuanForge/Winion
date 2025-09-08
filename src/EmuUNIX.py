Prototype = True


import os
def Emu_UNIX(commande):
    if commande[:5] == "clear":
        os.system("cls")
        return True
    else:
        return False
