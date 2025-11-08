import os
import hashlib

from Lib import Debug
from Lib.BlackHoles import  BlackHoles

def check_unit_SHA256(fichier, log: Debug.log.session = BlackHoles()):
    if os.path.isfile(fichier):
        sha256_hash = hashlib.sha256()
        with open(fichier, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    else:
        log.add(f"404={fichier}")
        return False


def check_sha256(demande, file_SHA256="checksums.sha256", log: Debug.log.session = BlackHoles()):
    log.add(f"demande={demande}, file_SHA256={file_SHA256}")
    Num_404 = 0
    Num_ERREUR = 0
    Num_OK = 0
    erreur = None
    if os.path.isfile(demande):
        file = demande
        rep = check_unit_SHA256(file)
        log.add("Stop")
        return rep
    elif os.path.isdir(demande):
        with open(os.path.join(demande, file_SHA256), 'r') as fichier:
            for ligne in fichier:
                ligne = ligne.strip()
                hash = ligne[:64]
                file = ligne[65:].replace("*", "")
                file = os.path.join(demande, file)
                if os.path.isfile(file):
                    rep = check_unit_SHA256(file)
                    if rep == hash:
                        log.add(f"{file} : OK")
                        Num_OK += 1
                    else:
                        log.add(f"{file} : ERREUR", "ERROR")
                        Num_ERREUR += 1
                        erreur = True
                else:
                    log.add(f"{file} : 404", "ERROR")
                    Num_404 += 1
                    erreur = True
    else:
        log.add("ERREUR demande = 404", "ERROR")
        return False
    log.add(f"OK={Num_OK}, 404={Num_404}, Erreur={Num_ERREUR}", "INFO")
    if erreur:
        return False
    else:
        return True