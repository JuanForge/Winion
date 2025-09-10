import io
import os
import sys
import time
import zipfile
import requests
import subprocess


from prompt_toolkit.shortcuts import button_dialog


from src.i18n import _
from src import network
from src.VERSION import VERSION
from src import sendnotification

def message():
            message = _("""
Votre application est en train de se mettre à jour vers la dernière version. 

Veuillez ne pas interrompre le processus de mise à jour. Assurez-vous que Winion reste ouvert et que l’ordinateur reste sous tension pendant toute la durée de la mise à jour.
L’interruption de ce processus pourrait corrompre Winion et entraîner un dysfonctionnement ou la perte de données.
Nous vous recommandons de patienter jusqu’à ce que la mise à jour soit complètement terminée avant de fermer l’application ou d’éteindre l’ordinateur.

Merci de patienter jusqu’à la finalisation complète de la mise à jour.""")
            return button_dialog(
                    title=_("⚠️ Mise à jour en cours ⚠️"),
                    text=f"{message} \n \n" + _("Souhaitez-vous continuer la mise à jour ?"),
                    buttons=[
                        (_("Annuler"), False),
                        (_("Oui"), True),
                    ]
                ).run()

class errors:
       class pipErrorCode(Exception): pass

def notification(newVersion: str, myVersion: str = VERSION.version()):
        message = [_("🚀 Nouvelle version disponible !"), "", _("Dernière version :") + " " + newVersion, _("Version actuelle :") + " " + myVersion, "", _("Nous vous recommandons de mettre à jour Winion pour profiter des dernières améliorations et correctifs.")]
        sendnotification.sendnotification("\n".join(message), _("🔄 Mise à jour disponible 🔄"))

url = "https://api.github.com/repos/JuanForge/Winion/releases/latest"
def _requests() -> dict:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

def _updateInstaller():
        os.makedirs(os.path.join("Temp", "Update"), exist_ok=True)
        assets = _requests().get("assets", [])
        for asset in assets:
            if asset["name"] in ["WinionSetup.exe", "Setup.exe"]:
                with open(os.path.join("Temp", "Update", "Setup.exe"), "wb") as f:
                       for chunk in network.download(asset["browser_download_url"]):
                              f.write(chunk)
                subprocess.run(os.path.abspath(os.path.join("Temp", "Update", "Setup.exe")), shell=True)
                print(_("Vous pouvez poursuivre l’installation dans le Setup.\n"
                        "Une fois celle-ci terminée, nous vous conseillons de fermer cette version de Winion (celle qui affiche ce message) afin de lancer la plus récente."))
                return True
        return False

def _update():
        IO = io.BytesIO()
        for chunk in network.download(_requests()["zipball_url"]):
                IO.write(chunk)
        zip_file = zipfile.ZipFile(IO)
        
        for zip_info in zip_file.infolist():
                if zip_info.is_dir():
                        continue
                parts = zip_info.filename.split("/", 1)
                if len(parts) == 2:
                    out = parts[1]
                else:
                    out = parts[0]
                
                if os.path.dirname(out):
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                with zip_file.open(zip_info) as src, open(out, "wb") as dst:
                        dst.write(src.read())
        if subprocess.run([sys.executable, "-m", "pip", "install", "--no-input", "--disable-pip-version-check", "-r", "requirements.txt"]).returncode == 0:
               sys.exit()
        else:
               raise errors.pipErrorCode()


def isUpdateAvailable():
        if _requests()["tag_name"] != VERSION.version():
                return True
        else:
                return False

def thread():
        while True:
                r = requests.get(url)
                r.raise_for_status()
                JSON = r.json()
                if JSON["tag_name"] != VERSION.version():
                        notification(JSON["tag_name"])
                time.sleep(180)