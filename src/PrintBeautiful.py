Prototype = True


from .colorV2 import color as c
def PrintBeautiful(texte):
    texte = texte.replace("True", f"{c.VERT}True{c.RESET}")
    texte = texte.replace("False", f"{c.ROUGE[0]}False{c.RESET}")
    return texte