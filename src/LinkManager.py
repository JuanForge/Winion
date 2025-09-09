Prototype = True

from Lib import Debug
from src.gofile import gofile
from Lib.BlackHoles import BlackHoles


def link2direct(lien, log: Debug.log.session = BlackHoles()):
    if lien.startswith("https://gofile.io/d/"):                                         # --------  GOFILE --------
        link, headers = gofile.get(lien)
        return link, headers
    
    elif lien.startswith("https://github.com/"):                                          # --------  GITHUB --------
        if "github.com" not in lien or "/blob/" not in lien:
            log.add("F.link2direct : Lien GitHub invalide", "WARNING")
            return link
        else:
            link = lien.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        return link
    
    else:
        log.add("F.link2direct : PAS DE CORRESPONDANCE", echo=False)
    return lien