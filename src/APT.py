import io
import os
import re
import sys
import json
import time
import zlib
import shlex
import base64
import shutil
import hashlib
import pathlib
import secrets
import requests
import rapidfuzz
import threading
import traceback
import subprocess

from typing import Optional
from natsort import natsorted
from operator import itemgetter
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.shortcuts import button_dialog


from Lib.Cache import Cache
from Lib.Debug import log


from src.i18n import _
from src import network
from src.colorV2 import color as c


from .color import *
from .Hash import Hash
from .Archive import Archive
from .VERSION import VERSION

import types


class errors:
    class InvalidEntrySource(Exception): pass
    class NotFound7zip(Exception): pass
    class ModuleTypeUnknown(Exception): pass

class apt:
    @staticmethod
    def session(configJson: dict,
                requestsSession: requests.Session,
                log: log.session,
                _Cache: Cache.session,
                outputConsole = print) -> 'apt._session':
        """
        ---- 🇫🇷 Français ----
        
        Crée une instance de gestionnaire de session pour le système APT personnalisé.
        
        Paramètres :
        - outputConsole (function) : Fonction utilisée pour afficher les messages de sortie dans la console. Par défaut, utilise la fonction `print`.
        - log (Optional[log._session]) : Instance du gestionnaire de logs. Utilisée pour enregistrer les événements via `log.add(...)`.
        - Cache (Optional[cache.Cache._session]) : Instance du système de cache. Utilisée pour stocker temporairement des informations (ex : `Cache.set(('apt', 'version'), version)`).
        
        ---- 🇺🇸 English ----
        
        Creates a session manager instance for the custom APT system.
        
        Parameters :
        - outputConsole (function): Function used to display output messages in the console. Defaults to the built-in `print`.
        - log (Optional[log._session]): Log manager instance. Used to record events via `log.add(...)`.
        - Cache (Optional[cache.Cache._session]): Caching system instance. Used to temporarily store information (e.g., `Cache.set(('apt', 'version'), version)`).
        """
        return apt._session(log=log, _Cache=_Cache, outputConsole=outputConsole,
        configJson=configJson, requestsSession=requestsSession)
    
    class _session:
        def __init__(self, configJson: dict,
                    requestsSession: requests.session,
                    outputConsole = print,
                    log: Optional[log.session] = None,
                    _Cache: Optional[Cache.session] = None):
            self._Cache = _Cache
            self.log = log
            self.conf = configJson
            self.outputConsole = outputConsole
            self.requestsSession = requestsSession
            #if _Cache:
            #    self._search = types.MethodType(self._Cache.wrapper(self._search), self)
        
        
        def _InvalideHashCLI(self):
            license_text = ANSI(f"""
                    {c.ROUGE[0]}{_("[SECURITE CRITIQUE]")}{c.RESET}
            {_("Le hash du module ne correspond pas à la signature attendue.")}
            
            {_('''Cette différence peut être due à :
                - un téléchargement incomplet ou corrompu
                - une version modifiée du module
                - un fichier malveillant''')}
            
                {_("Installer malgré tout peut compromettre votre système.")}
            {_("Voulez-vous tout de même continuer l’installation ?")}
            """)
            
            result = button_dialog(
                title=ANSI(f"{c.ROUGE[0]} {_('AVERTISSEMENT')} {c.RESET}"),
                text=license_text,
                buttons=[
                    (_("✘ Refusé"), False),
                    (_("✔ Continuer"), True),
                ]
            ).run()
            return result
        
        
        def _removeRoot(self, src, out):
            for root, dirs, files in os.walk(src):
                rel_path = os.path.relpath(root, src)
                target_dir = os.path.join(out, rel_path)
                
                os.makedirs(target_dir, exist_ok=True)
                
                for file in files:
                    s = os.path.join(root, file)
                    d = os.path.join(target_dir, file)
                    for i in range(5):
                        try:
                            shutil.move(s, d)
                            break
                        except Exception as e:
                            self.log.add(f"{s} -> {d} >> {e}", "ERROR")
                            if i == 4:
                                return False
                            time.sleep(1.5)
                            continue
            return True
        
        
        def _streamSource(self):
            for item in os.listdir("Source"):
                JSONs = os.path.join("Source", item)
                if os.path.isfile(JSONs):
                    if JSONs.endswith(".json"):
                        with open(JSONs, 'r') as file:
                            for entry in json.loads(file.read()):
                                entry["fileJson"] = JSONs
                                yield entry
        
        def _search(self, module: str = None, version: str = None, _keywords: str = None) -> dict:
            def _return(entry: dict) -> dict:
                return {'name': entry['name'],
                            'version': entry['version'],
                            'link': entry['link'],
                            'torrent': entry.get('torrent'),
                            'dependency': entry.get('dependency'),
                            'SHA256': entry["SHA256"],
                            "type": entry["type"],
                            "AllowRedirects": entry.get("AllowRedirects", False),
                            "removeRoot": entry.get("removeRoot", False),
                            "keywords": entry.get("keywords", []),
                            "dependencyKeys": entry.get("dependencyKeys", []),
                            "BuildExe": entry.get("BuildExe"),
                            "RemoveExe": entry.get("RemoveExe"),
                            "requirementsPython": entry.get("requirementsPython", "requirements.txt"),
                            "outName": entry.get("outName"),
                            "outFormat": entry.get("outFormat"),
                            "addPath": entry.get("addPath", [])}
            
            
            ALLversion = []
            for entry in self._streamSource():
                if module:
                    if entry['name'] == module:
                        if version:
                            if entry['version'] == version:
                                return _return(entry)
                        else:
                            ALLversion.append({"v": entry["version"], "f": entry["fileJson"], "entry": entry})
                elif _keywords:
                        if _keywords in entry.get("keywords", []):
                            return _return(entry)
                else:
                    raise "rien"
            if _keywords:
                return False
            elif ALLversion:
                return _return(natsorted(ALLversion, key=itemgetter("v"))[-1]['entry'])
            else:
                return None
        
        
        def _buildSource(self, module: str, version: str, exe: str) -> bool:
            result = subprocess.run(shlex.split(exe), capture_output=True, text=True, cwd=os.path.join("Module", module, version))
            self.log.add(f"return : {result.returncode}")
            if result.returncode == 0:
                self.log.add(result.stdout, "DEBUG")
                self.log.add(result.stderr, "DEBUG")
                return True
            else:
                self.log.add(result.stdout, "ERROR")
                self.log.add(result.stderr, "ERROR")
                return False
        
        
        def _addPath(self, folder: str) -> True:
            folder = os.path.abspath(folder)
            if os.environ["PATH"][-1] == ";":
                os.environ["PATH"] += folder
            else:
                os.environ["PATH"] += ";" + folder
            
            with open("PATH.txt", "a+", encoding="utf-8") as f:
                f.seek(0)
                lignes = [line.strip() for line in f.readlines()]
                if folder not in lignes:
                    f.write(folder + "\n")
            return True
        
        
        def _removePath(self, folder: str):
            with open("PATH.txt", "a+", encoding="utf-8") as f:
                f.seek(0)
                lignes = f.readlines()
                f.seek(0)
                f.truncate(0)
                for i in lignes:
                    if i.strip() != folder:
                        f.write(i)
        
        
        def search(self, data: str):
            list = []
            for entry in self._streamSource():
                s = matches = rapidfuzz.process.extract(
                    data,
                    [entry["name"]],
                    scorer=rapidfuzz.fuzz.ratio,
                    limit=1
                )[0]
                if s[1] >= 50:
                    list.append(entry["name"])
            print(", ".join(list))
            return True
        
        
        def update(self, source: str):
            print(source + "...")
            with open(os.path.join("Source", "__INI__.json"), "w", encoding="utf-8") as f:
                v = io.BytesIO()
                try:
                    for chunk in network.download(source, requestsSession=self.requestsSession, log=self.log):
                        v.write(chunk)
                except (network.errors.FailedRequest, network.errors.InvalideHTTP) as e:
                    self.log.add(e, "ERROR")
                    return False
                finally:
                    v.seek(0)
                    try:
                        json.loads(v.read().decode("utf-8"))
                    except Exception as e:
                        self.log.add(e, "ERROR")
                        return False
                    v.seek(0)
                    f.write(v.read().decode("utf-8"))
            return True
        
        
        def install(self, module: str, sessionAPT: 'apt._session', version: str = None, Parent: bool = True, reinstall=False) -> bool:
            """
            ---- 🇫🇷 Français ----
            
            Arguments :
            - Parent : 🚨​ NE PAS DÉFINIR MANUELLEMENT CET ARGUMENT. 🚨​
            
                - Il est réservé à un usage interne pour optimiser les appels récursifs de cette fonction.
            
            - version : Permet de spécifier une version particulière du module à installer.
            
                - Si aucune version n’est indiquée, la dernière version disponible sera automatiquement installée.
            
            ---- 🇺🇸 English ----
            
            Arguments :
            - Parent: 🚨​ DO NOT SET THIS ARGUMENT MANUALLY. 🚨​
            
                - It is intended for internal use only to optimize recursive calls made by this function.
            
            - version: Allows specifying a particular version of the module to install.
            
                - If no version is provided, the latest available version will be installed by default.
            
            """
            try:
                Cache = self._Cache
                log = self.log
                #print = self.outputConsole
                requestsSession = self.requestsSession
                
                log.add(f"module = {module}, version = {version}")
                
                start_time = time.time()
                
                module = self._search(module=module, version=version)
                self.log.add(f"Temps de la lecture {(time.time() - start_time) * 1000:.2f} ms.", "INFO")
                if not module:
                    print(c.ROUGE[2] + _("VERSION OU MODULE INTROUVABLE") + c.RESET)
                    return False
                
                if reinstall or not os.path.isfile(os.path.join("Module", module["name"], module['version'] + ".config", "index.apt.json")):
                    for i in module["dependencyKeys"]:
                        deb = self._search(module=None, version=None, _keywords=i)
                        if deb:
                            if not self.install(deb["name"], sessionAPT=self, version=None, reinstall=reinstall):
                                return False
                        else:
                            print(c.ROUGE[2] + _("AUCUN MODULE POUR LA CLE :") + i + c.RESET)
                            return False
                    
                    
                    print(f"[{module['name']}] Dependency : ", end='')
                    if module['dependency']:                                                      #--------  dependency  --------
                        print(_("OUI"))
                        for i in module['dependency']:
                            if '==' in i:
                                name, version = i.split('==', 1)
                                self.install(name, version=version, sessionAPT=self, reinstall=reinstall)
                            else:
                                self.install(name, version=None, sessionAPT=self, reinstall=reinstall)
                    else:
                        print(_("NON"))
                    
                        if 'InstallOptimizer' in globals():
                            if InstallOptimizer.version() == '0.001': # type: ignore
                                if hasattr(InstallOptimizer, 'presence'): # type: ignore
                                    module, Version = InstallOptimizer.presence(module, Version) # type: ignore
                                    log.add("InstallOptimizer : OK")
                            else:
                                log.add("InstallOptimizer : non compatible", level='WARNING')
                        else:
                            log.add("InstallOptimizer : non disponible")
                        
                        print(f"[{module['name']}] {module['name']} == {module['version']}")
                        if not os.path.isfile(f"Cache\\{module['name']}=={module['version']}.7z"):
                            log.add(f"[{module['name']}] Cache : NON")
                            tempName = secrets.token_hex(16)
                            os.makedirs(f"Temp\\{tempName}", exist_ok=True)
                            tempDir = f"Temp\\{tempName}"
                            
                            print(f"[{module['name']}] {_('Methode')} : ", end='')
                            if module.get("torrent") and self.conf['torrent']['use']:
                                raise
                                print('torrent')
                                rep = torrent.download(torrent=zlib.decompress(base64.b64decode(module['torrent'])), output_dir=f"{os.getcwd()}\\Temp\\{tempDir}")
                                if rep:
                                    os.rename(f"Temp\\{tempDir}\\__Main__.7z", f"Temp\\{module['name']}=={module['version']}.7z.001")
                            else:
                                print(f'HTTP')
                                print(f"[{module['name']}] ModuleType:" + str(module["type"]))
                                
                                if module["type"] == 0:
                                    out = open(f"{tempDir}\\{module['name']}=={module['version']}.7z.001", "wb")
                                elif module['type'] == 1:
                                    out = open(f"{tempDir}\\{module['name']}=={module['version']}.exe", "wb")
                                elif module['type'] == 2:
                                    raise "INVALIDE TYPE 2"
                                elif module['type'] == 3:
                                    out = open(f"{tempDir}\\{module['name']}=={module['version']}.exe", "wb")
                                else:
                                    raise errors.ModuleTypeUnknown(str(module['type']))
                                
                                SHA256 = hashlib.sha256()
                                try:
                                    for chunk in network.download(module['link'], requestsSession=requestsSession,
                                                                log=self.log, AllowRedirects=module.get("AllowRedirects", False), leave=True, prefix=f"[{module['name']}]"):
                                        SHA256.update(chunk)
                                        out.write(chunk)
                                except (network.errors.FailedRequest, network.errors.InvalideHTTP):
                                    print(f"[{module['name']}] {_('Téléchargement...')}" + ROUGE[2] + _("ERREUR") + RESET)
                                    return False
                                finally:
                                    outName = out.name
                                    out.close()
                                
                                print(f"[{module['name']}] {_('Téléchargement...')}" + VERT + _("OK") + RESET)
                                
                                print(f"[{module['name']}] {_('Test du Hash...')}", end='', flush=True)
                                if SHA256.hexdigest() != module["SHA256"]:
                                    print(f"{ROUGE[0]}{_('INVALIDE')}{RESET}")
                                    if not self._InvalideHashCLI():
                                        return False
                                else:
                                    print(f"{VERT}{_('VALIDE')}{RESET}")
                                
                                outModule = os.path.join("Module", module['name'], module['version'])
                                
                                os.makedirs(outModule, exist_ok=True)
                                os.makedirs(os.path.join(outModule + ".tmp"), exist_ok=True)
                                os.makedirs(os.path.join(outModule + ".config"), exist_ok=True)
                                
                                with open(os.path.join(outModule + ".config", "index.apt.json"), "w", encoding="utf-8") as f:
                                    f.write(json.dumps(module))
                                
                                
                                if module["type"] == 0:
                                    print(f"[{module['name']}] {_('Décompression de larchive...')}", end='', flush=True)
                                    if Archive.unzip(outName, outModule + ".tmp", log=self.log):
                                        print(f"{VERT}OK{RESET}")
                                        
                                        print(f"[{module['name']}] {_('Test des Hash...')}", end='', flush=True)
                                        
                                        if os.path.isfile(os.path.join(outModule + ".tmp", "checksums.sha256")):
                                            if Hash.check_sha256(os.path.join(outModule + ".tmp"), "checksums.sha256", log=self.log):
                                                print(f"{VERT}OK{RESET}")
                                            else:
                                                print(f"{ROUGE[0]}ERROR{RESET}")
                                        else:
                                            print(f"{ORANGE}(404 : checksums.sha256){RESET}")
                                        
                                        print(f"[{module['name']}] {_('Migration...')}", end='', flush=True)
                                        if module["removeRoot"]:
                                            rep = self._removeRoot(os.path.join(outModule + ".tmp", module["removeRoot"]), outModule)
                                        else:
                                            rep = self._removeRoot(os.path.join(outModule + ".tmp"), outModule)
                                        if rep:
                                            print(f"{VERT}OK{RESET}")
                                        else:
                                            print(f"{ROUGE[0]}ERROR{RESET}")
                                            return False
                                        
                                        if os.path.isfile(os.path.join(outModule, module["requirementsPython"])):
                                            print(f"[{module['name']}] requirements (python)...", end='', flush=True)
                                            cmd = [
                                                sys.executable,
                                                "-m",
                                                "pip",
                                                "install",
                                                "--no-input",
                                                "--disable-pip-version-check",
                                                "-r",
                                                module["requirementsPython"]
                                            ]
                                            result = subprocess.run(cmd, capture_output=True, text=True, cwd=outModule)
                                            self.log.add(f"return : {result.returncode}")
                                            if result.returncode == 0:
                                                self.log.add(result.stdout, "DEBUG")
                                                self.log.add(result.stderr, "DEBUG")
                                                print(c.VERT + "OK" + c.RESET)
                                            else:
                                                self.log.add(result.stdout, "ERROR")
                                                self.log.add(result.stderr, "ERROR")
                                                print(c.ROUGE[2] + "ERROR" + c.RESET)
                                                return False
                                        
                                        if module["BuildExe"]:
                                            print(f"[{module['name']}] {_('Compilation...')}", end='', flush=True)
                                            if self._buildSource(module=module["name"], version=module["version"], exe=module["BuildExe"]):
                                                print(c.VERT + "OK" + c.RESET)
                                            else:
                                                print(c.ROUGE[2] + "ERROR" + c.RESET)
                                                return False
                                        
                                        self._addPath(outModule)
                                        for i in module["addPath"]:
                                            self._addPath(os.path.join(outModule, i))
                                    else:
                                        print(f"{ROUGE[0]}ERROR{RESET}")
                                        return False
                                elif module['type'] == 1:
                                    if module["outName"] and module["outFormat"]:
                                        getout = os.path.join(outModule, module["outName"] + "." + module["outFormat"])
                                    else:
                                        getout = os.path.join(outModule, module["name"])
                                    shutil.move(outName, getout)
                                    return True
                                elif module['type'] == 3:
                                    subprocess.run([os.path.abspath(outName)], shell=False)
                                    return True
                                
                                return True
                else:
                    print(f"[{module['name']}] {VERT}{_('déja installé')}{RESET}")
                    return True
            except KeyboardInterrupt:
                return False
    
    
    
        def remove(self, module, version):
            for root, dirs, files in os.walk(os.path.join("Module", module, version)):
                for file in files:
                    os.remove(os.path.join(root, file))
            self._removePath(os.path.abspath(os.path.join("Module", module, version)))
            for i in json.loads(open(os.path.join("Module", module, version + ".config", "index.apt.json"), "r", encoding="utf-8").read()).get("addPath", []):
                self._removePath(os.path.abspath(i))
            return True