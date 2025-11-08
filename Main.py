import sys, os
if False == True:
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
else:
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

import time
start_time = time.monotonic_ns()
import io
import os
import sys
import json
import time
import zlib
import polib
import shlex
import atexit
import locale
import random
import signal
import struct
import shutil
import difflib
import gettext
import hashlib
import secrets
import tarfile
import zipfile
import argparse
import platform
import pyfiglet
import requests
import tempfile
import miniupnpc
import pyperclip
import threading
import traceback
import subprocess

from pathlib import Path
from rich.panel import Panel
from rich.table import Table
from datetime import datetime
from pyfiglet import FigletFont
from rich.console import Console
from yaspin import yaspin, spinners
from concurrent.futures import ThreadPoolExecutor
from prompt_toolkit.shortcuts import button_dialog

from Lib.Cache import Cache
from Lib.Debug import log as NewLog

from src import api
from src import APT
# from src import Tor
from src import Help
from src import i18n
#from src import zip7
from src import update
from src.i18n import _
from src import Archive
from src import EmuUNIX
from src import VERSION
from src import settings
from src import trayservice
from src import TraceInjector
from src import PrintBeautiful
from src import input as _input
from src import commande as exe
from src.network import download
from src.colorV2 import color as c
from src.LinkManager import link2direct
from src.importDynamic import importDynamic
from src.sendnotification import sendnotification

if platform.system() == "Windows":
    import ctypes
    import winreg
    import win32console # type: ignore
    import win32api  # type: ignore

time_load_module = time.monotonic_ns() - start_time

# with yaspin(spinner=spinners.Spinners.dots12, text="Chargement...", color="red", timer=True) as e:
def main(session: dict):
    global _
    threads = []
    STOP = [False]
    exe.title("Winion")
    #sys.path.insert(0, "./Lib")
    os.environ["PIP_CONFIG_FILE"] = os.path.abspath("./pip.ini")
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    
    if os.path.isfile("index"):
        with open("index", "rb") as f:
            if struct.unpack("!B", f.read(1))[0] != 0:
                button_dialog(
                    title=_("Avertissement"),
                    text=_("Le programme a été interrompu brutalement lors du dernier lancement.\n"
                            "Il est possible que certaines données n’aient pas été sauvegardées correctement.\n"
                            "Merci de signaler ce problème au développeur pour qu’il puisse investiguer."),
                    buttons=[
                        (_("✔ Compris"), True),
                    ]
                ).run()
    with open("index", "wb") as f:
        f.write(struct.pack("!B", 1))
    
    
    for i in ['settings.json', 'Bin/']:
        if not os.path.exists(i):
                print(f"{c.ROUGE[3]}[ERROR]{c.RESET} : {i} : {c.ROUGE[3]}404{c.RESET}")
                sys.exit(44)
    configJson = settings.settings.load()
    
    with open("settings.json", "r+") as f:
        JSON = json.load(f)
        if not JSON['LICENSEagree'] == True:
            
            console = Console()
            
            license_text = _("""
            Creative Commons BY-NC-ND 4.0
            
            Utilisation autorisée :
            - SANS usage commercial ;
            - SANS modification ;
            - AVEC attribution.
            
            https://creativecommons.org/licenses/by-nc-nd/4.0/deed.fr
            
            © 2025 JuanForge pour le projet Winion — Ce projet est sous licence Creative Commons Attribution - Non Commercial - Pas de Modification 4.0 International (CC BY-NC-ND 4.0).
            Voir le fichier LICENSE ou https://creativecommons.org/licenses/by-nc-nd/4.0/deed pour les détails.
            """)
            
            console.print(Panel(license_text, title=_("Licence")))
            
            if button_dialog(
                    title=_("Accepter la licence"),
                    text=f"{license_text} \n \n" + _("Souhaitez-vous continuer l'installation ?"),
                    buttons=[
                    (_("✔ Compris"), True),
                    (_("✘ Refusé"), False),
                ]
                ).run():
                    console.print(f"[bold green]✔ {_('Licence acceptée.')}[/]")
                    f.seek(0)
                    JSON['LICENSEagree'] = True
                    json.dump(JSON, f, indent=4)
                    f.truncate()
            else:
                    console.print(f"[bold red]✘ {_('Licence refusée.')} [/]")
                    sys.exit(152)
    
    
    if configJson['TraceInjector']['DEBUG']['enable'] == True:
        session['TraceInjector'] = TraceInjector.session(open(f"TraceInjector.json", "w"), TypeJSON=4, addExecute=True)
        
        sys.settrace(session['TraceInjector'].tracer)
        threading.settrace(session['TraceInjector'].tracer)
    
    
    session['ThreadPool'] = ThreadPoolExecutor(max_workers=configJson['Thread']['ThreadPoolExecutor'])
    
    
    
    
    global clientTor # Permet de tenir la connexion entre le process et lui de tor
    
    
    parser = argparse.ArgumentParser(
        description=_("Programme principal."),
        allow_abbrev=False
    )
    
    group = parser.add_mutually_exclusive_group(required=False)
    
    group.add_argument('--benchmark', action='store_true', help=_("Exécute un benchmark interne."))
    group.add_argument('--boot', action='store_true', help=_("Exécute les tests unitaires."))
    group.add_argument('--version', action='store_true', help=_("Afficher la version et build"))
    parser.add_argument(
            '--commande',
            type=str,
            help=_('Commande à exécuter')
        )
    
    
    args, unknown = parser.parse_known_args()
    if unknown:
        print(f"{_('Erreur : arguments non reconnus')} : {' '.join(unknown)}", file=sys.stderr)
        sys.exit(190)
    
    def outVersion():
        print(f"Version : {c.VERT}{VERSION.VERSION.version()}{c.RESET}")
        print(f"Build : {c.BLEU[2]}{VERSION.VERSION.build()}{c.RESET}")
        print(f"Release : {c.ORANGE}{VERSION.VERSION.release()}{c.RESET}")
        return True
    
    if args.version:
        outVersion()
        sys.exit(0)
    
    if args.boot:
        if not configJson['ReleaseType'] == 'DEV0':
            for folder in ['Temp', 'Source', 'Logs', 'Module', 'Cache', 'Completist', 'Lib']: # Builder\\Lib Builder\\H Task\\Boot
                os.makedirs(folder, exist_ok=True)
        errorlevel = False
        for file_name in os.listdir("Temp"):
            file_path = os.path.join("Temp", file_name)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    errorlevel = True
                    print(f"{c.ROUGE[0]} {e} {c.RESET}", end='', flush=True)
        if errorlevel:
            print(f"{c.ROUGE[0]}ERREUR : DEL Temp{c.RESET}")
            sys.exit(217)
        
        #for fichier in os.listdir("Task\\Boot"):
        #    if fichier.endswith(".bat"):
        #        fichier = os.path.join("Task\\Boot", fichier)
        #        os.system(f"{fichier}")
    
    session['requests'] = requests.Session()
    #session['requests'].verify = False
    #session['requests'].options(timeout=(10, 20), verify=False)

    Rtime = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    session['log'] = NewLog.session(open(f"{os.path.join('Logs', f'{Rtime}_{secrets.token_hex(8)}.log')}", "w", encoding="utf-8"),
                                        NewLog.level._lv0DEBUG_)
    
    session["log"].add(f"Time to load all module : {time_load_module / 1_000_000} ms", "INFO")
    
    session['cache'] = Cache.session(sessionLog=session['log'])
    session['cache'].HEADER = "Winion" + str(VERSION.VERSION.VERSION) + str(VERSION.VERSION.BUILD)
    
    def load_cache(CacheS: Cache.session, log: NewLog.session):
        try:
            CacheModeFoler = False
            if CacheModeFoler:
                files = sorted(Path("Cache").glob("Cache-*.WCP"), reverse=True)
                if not files:
                    return False
                
                f = files[0]
                print(f)
                if f.stat().st_size == 0:
                    log.add(_("Fichier vide, ignoré."), "INFO")
                    return True
                
                log.add(f"DEBUG : Cache : load == {f.name}", "INFO")
                
                with f.open('rb') as fd:
                    CacheS.load(fd)
                
                return True
            else:
                if os.path.isfile("Cache.WCP"):
                    with open("Cache.WCP", "rb") as f:
                        CacheS.load(f)
        except Cache.errors.InvalidSignature:           
            button_dialog(
                title=_("Erreur Cache"),
                text=_("Erreur dans la Signature du cache !"),
                buttons=[
                    (_("✔ Compris"), True),
                ]
            ).run()
        
        except Exception as e:
                log.add(f"Erreur de chargement du cache : {e}", "CRITICAL")
                sys.exit(271)
    load_cache(session["cache"], session["log"])
    
    if configJson['trayservice'] == True:
        session["trayservice"] = trayservice.trayservice.session(session["cache"], STOP=STOP)
        
        threading.Thread(target=session["trayservice"].Execute, daemon=True).start()
    
    
    session['requests'].headers.update({
        "User-Agent": configJson['requests']['User-Agent']
    })
    
    
    if configJson['requests']['proxy']:
        session['requests'].proxies.update({
            "http": f"socks5h://{configJson['requests']['proxy']}",
            "https": f"socks5h://{configJson['requests']['proxy']}"
        })
    
    for domain, name, value in configJson['requests']['cookie']:
        session['requests'].cookies.set(name, value, domain=domain)
    
    
    
    session["apt"] = APT.apt.session(log=session['log'], _Cache=session['cache'],
                                    configJson=configJson,
                                    requestsSession=session['requests'])
    
    if args.benchmark:
        startG = time.perf_counter()
        n = 256 * 256
        repetitions = 4
        durations = []
        print(_("Exécution du benchmark..."))
        for i in range(repetitions):
            start = time.perf_counter()
            for i in range(n): # 256 * 256 * 256 * 24
                nombre1 = int(str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(255)))
                nombre2 = int(str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(255)))
                nombre3 = int(str(random.randint(1, 9)) + ''.join(str(random.randint(0, 9)) for _ in range(255)))
                if nombre1 > nombre2 > nombre3:
                    pass
                pass
            end = time.perf_counter()
            durations.append(end - start)
        average = sum(durations) / len(durations)
        print(f"{_('Temp de benchmark')} : {average:.20f} secondes")
        print(f"Temp d'execution : {time.perf_counter() - startG:.5f} secondes")
        sys.exit(0)
    
    elif args.boot:
        if platform.system() == "Windows":
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Console")
                winreg.SetValueEx(key, "VirtualTerminalLevel", 0, winreg.REG_DWORD, 1) # shell  :  reg add "HKEY_CURRENT_USER\Console" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f
                winreg.CloseKey(key)
                print(_("✅ Couleurs ANSI activées avec succès."))
            except Exception as e:
                print(_("❌ Erreur lors de la modification du registre") + f" : {e}")
                sys.exit(331)
            
            #Tor.install(log=session["log"])
            
            #clientTor = Tor.launch()
            #time.sleep(2)
            
            def download_boot(url, headers, prefix, out) -> bool:
                with open(out, 'wb') as file:
                    for chunk in download(url,
                                        requestsSession=session["requests"],
                                        log=session["log"],
                                        prefix=prefix,
                                        speedNetwork=10 * 1024 * 1024,
                                        leave=True,
                                        headers=headers):
                        file.write(chunk)
            
            for url, prefix, out in [
                                        #(link2direct('https://gofile.io/d/qRYt14'), "File:libcrypto-1_1-x64.dll", "Bin\\libcrypto-1_1-x64.dll"),
                                        #(link2direct('https://gofile.io/d/6jbWau'), "File:NewGen.json", "Source\\NewGen.json"),
                                        #(link2direct('https://gofile.io/d/3LhdlN'), "File:commande.txt", "Completist\\commande.txt"),
                                        #(link2direct('https://gofile.io/d/URy4zn'), "File:commande - WI.txt", "Completist\\commande - VI.txt"),
                                        #(link2direct('https://gofile.io/d/gu6uXm'), "File:module.txt", "Completist\\module.txt"),
                                        (("https://github.com/transmission/transmission/releases/download/4.0.6/transmission-4.0.6-qt5-x64.msi", ""), "transmission", "Temp\\transmission-4.0.6-qt5-x64.msi"),
                ]:
                futures = []
                futures.append(session['ThreadPool'].submit(download_boot, url[0], url[1], prefix, out))
            for i in futures:
                i.result()
            Archive.Archive.unzip(os.path.join("Temp", "transmission-4.0.6-qt5-x64.msi"), os.path.join("Temp", "transmission"), log=session['log'])
            #zip7.install(sessionLog=session["log"])
            sys.exit(0)
    
    #clientTor = Tor.launch()
    
    def sendAD():
        while True:
            time.sleep(60 * 3)
            sendnotification(_("💜 Si Winion vous plaît, vous pouvez soutenir le projet en tapant") + " : donation", "❤️ Winion Donation ❤️")
    
    threads.append(threading.Thread(target=sendAD, daemon=True).start())
    threads.append(threading.Thread(target=update.thread, daemon=True).start())

    if configJson["api"]["enable"]:
        print(f"API : {configJson["api"]["host"]}:{configJson["api"]["port"]}")
        session["api"] = api.api(host=configJson["api"]["host"], port=configJson["api"]["port"], fork=True, reload=False)
        session["api"].run()
    else:
        print(f"API : {c.ORANGE}disable{c.RESET}")
    
    if os.path.isfile("PATH.txt"):
        with open("PATH.txt", "r", encoding="utf-8") as f:
            for i in f.readlines():
                if os.environ["PATH"][-1] == ";":
                    os.environ["PATH"] += i.strip()
                else:
                    os.environ["PATH"] += ";" + i.strip()
    
    ArgumentExit = False
    
    session["log"].add(f"PID : {os.getpid()}", "INFO")
    
    if not args.commande:
        def Menu() -> str:
            sortie = []
            try:
                import dearpygui.dearpygui as dpg # type: ignore
                SUPPORT_GUI = f"{c.VERT} {_('OUI')} {c.RESET}"
            except ImportError:
                SUPPORT_GUI = f"{c.ROUGE[2]} {_('NON')} {c.RESET}"
            
            font = random.choice(['3-d', '3d-ascii', '3d_diagonal', '4max', '5lineoblique', 'alligator2', 'amc_aaa01', 'ansi_shadow', 'avatar', 'basic', 'big',
                                'big_money-ne', 'big_money-nw', 'blocky', 'bloody', 'broadway', 'calgphy2', 'chiseled', 'colossal', 'dos_rebel', 'electronic',
                                'fraktur', 'isometric3', 'nscript', 'poison', 'speed', 'the_edge'])
            sortie.append(c.BLEU[1])
            sortie.append(pyfiglet.figlet_format("Winion!", font=font))
            sortie.append(c.RESET)
            
            sortie.append(_("Support GUI") + " : " + SUPPORT_GUI)
            print("\n".join(sortie))
            
            
            def upnpMapPorts():
                upnp = miniupnpc.UPnP()
                upnp.discoverdelay = 800
                console = Console()
                table = Table(title=_("État de la découverte et redirection UPnP"), show_edge=True, border_style="bright_blue")
                table.add_column(_("Étape"), style="bold cyan")
                table.add_column(_("Résultat"), style="bold yellow")
                
                
                try:
                    if upnp.discover():
                        table.add_row(_("Découverte UPnP"), f"[green]✅[/green]")
                        
                        try:
                            upnp.selectigd()
                            table.add_row(_("Sélection routeur IGD"), "[green]✅[/green]")
                            
                            try:
                                #table.add_row("Redirection port", f"Tentative de {port_externe}/{protocol} → {port_interne}")
                                if upnp.addportmapping(51413, 'UDP',upnp.lanaddr, 51413, "51413", ''
                                        ) and upnp.addportmapping(51413, 'TCP',upnp.lanaddr, 51413, "51413", ''): ### ! AJOUTER LOG
                                    table.add_row(_("Résultat redirection"), "[green]✅[/green]")
                                
                                else:
                                    table.add_row(_("Résultat redirection"), "[red]" + _("❌ Échec de la redirection") + "[/red]")
                            
                            except Exception as e:
                                table.add_row(_("Résultat redirection"), f"[red]" + _("Erreur ( voir Log )") + "[/red]")
                        
                        except Exception as e:
                            table.add_row(_("Sélection routeur IGD"), f"[red]" + _("❌ ( voir Log )") + "[/red]")
                    
                    else:
                        table.add_row(_("Découverte UPnP"), "[red]" + _("❌ Aucun périphérique UPnP détecté") + "[/red]")
                
                except Exception as e:
                    table.add_row(_("Découverte UPnP"), "[red]" + _("❌ ( voir Log )") + "[/red]")
            
                console.print(table)
            upnp = upnpMapPorts()
        
        upnp = Menu()
        
        
    while not STOP[0]:
        if args.commande:
            if ArgumentExit:
                sys.exit()
        
        print(f"{c.VERT}┌──({c.BLEU[0]}Winion{c.ROUGE[0]}@{c.BLEU[0]}DESKTOP-{platform.system()}{c.VERT})-[{c.BLANC}{os.getcwd()}{c.VERT}]")
        print(f"{c.VERT}└─{c.BLEU[0]}${c.RESET}", end='')
        
        if not args.commande:
            rep = _input.input_()
        else:
            rep = args.commande
        
        if rep == "":
            if args.commande:
                exit()
            else:
                continue
        session["log"].add(f"input : {rep}")
        
        if args.commande:
            ArgumentExit = True
        
        for rep in rep.split(" && "):
            rep = str(rep)
            
            
            if rep.lower() == "version":
                outVersion()
                continue
            
            elif rep.lower() == "update":
                if update.isUpdateAvailable():
                    if update.message():
                        update._updateInstaller()
                continue
            
            elif rep.lower() == "flush":
                session["log"].flush()
                continue
            
            elif rep.lower().startswith("addlang"):
                rep = rep.strip().split()
                if len(rep) >= 2:
                    if rep[1] == "--force":
                        if len(rep) >= 3:
                            if os.path.isfile(os.path.join("./Languages", rep[2], "LC_MESSAGES", "Winion.mo")):
                                os.makedirs(os.path.join("./Languages", "default", "LC_MESSAGES"), exist_ok=True)
                                open(os.path.join("./Languages", "default", "LC_MESSAGES", "Winion.mo"), "wb").write(
                                    open(os.path.join("./Languages", rep[2], "LC_MESSAGES", "Winion.mo"), "rb").read()
                                )
                                print("✅")
                                continue
                            else:
                                sys.stderr.write("not found ISO" + "\n")
                                continue
                        else:
                            sys.stderr.write("--force <ISO installed>" + "\n")
                            continue
                    elif rep[1] == "--lang-used":
                        sys.stdout.write(_("Vous utiliser l'ISO ->") + str(i18n.LANG).upper() + "\n")
                        continue
                    else:
                        file = rep[1]
                else:
                    try:
                        import dearpygui.dearpygui as dpg # type: ignore
                        import tkinter as tk
                        from tkinter import filedialog
                        
                        root = tk.Tk()
                        root.iconbitmap("./Assets/icon.ico")
                        root.withdraw()
                        
                        file = filedialog.askopenfilename(
                            title=_("Sélectionnez un fichier .MO."),
                            filetypes=[("Fichiers MO", "*.mo")]
                        )
                    except ImportError:
                        print(_("Vous devez spécifier le fichier .MO en argument."))
                        print("❌")
                        continue
                if file and os.path.isfile(file):
                    mobyte = open(file, "rb").read()
                    lang = polib.mofile(file).metadata.get("language", None)
                    if lang:
                        os.makedirs(os.path.join("./Languages", lang, "LC_MESSAGES"), exist_ok=True)
                        open(os.path.join("./Languages", lang, "LC_MESSAGES", "Winion.mo"), "wb").write(mobyte)
                        session["log"].add(f"language add : {lang}", "INFO")
                        print(_("La langue a été intégrée avec succès !"))
                        print("✅")
                    else:
                        print("❌")
                else:
                    print("❌")
                continue
            
            elif rep.lower() == "apt update":
                if session["apt"].update(configJson["apt"]["source"][0]):
                    print(c.VERT + _("OK") + c.RESET)
                else:
                    print(c.ROUGE[2] + _("ERREUR") + c.RESET)
                continue
            
            elif rep.lower().startswith("apt remove"):
                if "==" in rep.lower():
                    name, version = rep[10:].strip().lower().split('==', 1)
                    if session["apt"].remove(name, version):
                        print(_("OK"))
                    else:
                        print(_("ERREUR"))
                else:
                    print(_("Veuillez spécifier une version."))
                continue
            
            elif rep.startswith("apt install"):
                LISTE_MODULE_INSTALLER_OK = []
                LISTE_MODULE_INSTALLER_ERREUR = []
                if "--reinstall" in rep:
                    rep = rep.replace("--reinstall", "")
                    reinstall = True
                else:
                    reinstall = False
                parts = rep[12:].split()
                for i in parts:
                    if '==' in i:
                        name, version = i.split('==', 1)
                        if session['apt'].install(module=name, version=version, sessionAPT=session["apt"], reinstall=reinstall):
                            LISTE_MODULE_INSTALLER_OK.append(f"{name}=={version}")
                        else:
                            LISTE_MODULE_INSTALLER_ERREUR.append(f"{name}=={version}")
                    else:
                        if session['apt'].install(module=i, sessionAPT=session["apt"], reinstall=reinstall):
                            LISTE_MODULE_INSTALLER_OK.append(f"{i}")
                        else:
                            LISTE_MODULE_INSTALLER_ERREUR.append(f"{i}")
                
                print(c.VERT + _("Installés : ") + ", ".join(LISTE_MODULE_INSTALLER_OK) + c.RESET)
                print(c.ROUGE[0] + _("Non installés : ") + ", ".join(LISTE_MODULE_INSTALLER_ERREUR) + c.RESET)
                continue
            
            elif rep.startswith("apt search "):
                session["apt"].search(rep[11:])
                continue
            
            elif rep[:7] == "history":
                with open(".history_SHELL", "r", encoding="utf-8") as fichier:
                    for ligne in fichier:
                        print(ligne)
                        continue
            
            elif rep.lower() == "donation":
                pyperclip.copy(configJson['xmrAddress'])
                print(_("L’adresse a été copiée, il ne reste plus qu’à la coller."))
                print(_("Et au cas où, la voici en bas."))
                print(configJson['xmrAddress'])
                try:
                    import dearpygui.dearpygui as dpg # type: ignore
                    import qrcode # type: ignore
                    import dearpygui.dearpygui as dpg # type: ignore
                    from PIL import Image
                    
                    img = qrcode.make(configJson['xmrAddress']).convert("RGBA")
                    w, h = img.size
                    data = img.tobytes()
                    
                    dpg.create_context()
                    with dpg.texture_registry():
                        dpg.add_static_texture(w, h, data, tag="qr")
                    
                    with dpg.window(label="", no_title_bar=True, no_move=True, no_resize=True, no_background=True, width=w, height=h):
                        dpg.add_image("qr")
                    
                    dpg.create_viewport(title="QR Code", width=w+20, height=h+42)
                    dpg.setup_dearpygui()
                    dpg.show_viewport()
                    dpg.start_dearpygui()
                    dpg.destroy_context()
                except ImportError:
                    pass
                os.startfile(f"monero:{configJson['xmrAddress']}")
                continue
            
            elif rep[:10] == "apt update":
                session['apt'].update()
                continue
            
            elif rep[:14] == "apt get-source":
                session["apt"].apt_get_source()
                continue
            
            elif rep[:6].lower() == "start ":
                arguments = shlex.split(rep[6:].strip(), posix=True)
                module = arguments[0]
                del arguments[0]
                Racine = f"{os.path.join(os.getcwd(), 'Module', module)}"
                print(Racine)
                if os.path.isdir(Racine):
                    version = json.loads(open(os.path.join(Racine, "index.json")).read())["lastVersion"]
                    
                    py = os.path.join(Racine, version, 'main.py')
                    cmd = shlex.join([sys.executable, py] + arguments)
    
                    print(cmd)
                    
                    if os.path.isfile(py):
                        with yaspin(spinner=spinners.Spinners.material, text=_("Process en cours..."), color="red", timer=True) as e:
                            if platform.system() == "Linux":
                                proc = subprocess.Popen([
                                    "gnome-terminal", 
                                    "--", 
                                    "bash", 
                                    "-c", 
                                    cmd + "; exec bash"
                                ], cwd=os.path.join(Racine, version))
                            elif platform.system() == "Windows":
                                CREATE_NEW_CONSOLE = 0x00000010
                                proc = subprocess.Popen([cmd], creationflags=CREATE_NEW_CONSOLE, cwd=os.path.join(Racine, version))
                            else:
                                raise "668"
                            while proc.poll() is None:
                                time.sleep(1)
                            else:
                                e.write(_(f"Process terminé avec le code : ") + str(proc.poll()))
                        continue
                """
                module = rep[6:].strip()
                Racine = f"{ROOT}\\Module"
            
                for item in os.listdir(Racine):
                    dossier = os.path.join(Racine, item)
            
                    if os.path.isdir(dossier):
                        py = os.path.join(dossier, 'Start.py')
                        if os.path.isfile(py):
                            module = importDynamic.Script(py)
                            module.Start.Start()
                """
            
                """
                if rep[:11] == "apt upgrade":
                    module = rep[12:]
                    if module == "":
                        apt.upgrade()
                    else:
                        apt.upgrade(module)
                    continue
                
                if rep[:10] == "apt remove":
                    module = rep[11:]
                    if module == "":
                        print("PEUT PAS ETRE VIDE")
                    else:
                        apt.remove(module)
                    continue
                
                if rep[:15] == "check integrity":
                    module = rep[16:]
                    if module == "":
                        apt()
                    else:
                        apt(module)
                    continue
                """
                
            elif rep[:6] == "REBOOT":
                return "REBOOTcode"
            
            elif rep[:10] == "injection:":
                exec(rep[10:])
                continue
            
            elif rep[:7] == "inject:":
                exec(rep[7:])
                continue
            
            elif rep.lower() == "exit":
                sys.exit(0)
            
            elif rep.upper() == "HELP":
                print(Help.Help_Commande())
            
            elif rep[:3].upper() == "OS:":
                commande = rep[3:]
                errorlevel = os.system(commande)
                print(f"OS : RETURNE [{errorlevel}]")
                if errorlevel == 50:
                    print("EXIT !!")
                    sys.exit()
            
            elif EmuUNIX.Emu_UNIX(rep) == True:
                continue
            
            else:
                reps = shlex.split(rep, posix=True)
                exet = shutil.which(reps[0])
                if exet:
                    if True == True:
                        session["log"].add(reps)
                        subprocess.run(reps, cwd=os.path.dirname(exet))
                    else:
                        subprocess.run(rep, shell=True)
                else:
                    print(c.ROUGE[0] + "Unknown command" + c.RESET)
                    with open(os.path.join("completist", "commande.txt"), "r", encoding="utf-8") as fichier:
                        COMMANDS = [ligne.strip() for ligne in fichier if ligne.strip() and not ligne.startswith("#")]
                    correspondances = difflib.get_close_matches(rep, COMMANDS, n=5, cutoff=0.6)
                    if correspondances:
                        print("\n".join(correspondances))
    else:
        sys.exit()

if __name__ == "__main__":
    REBOOTcode = True
    while REBOOTcode:
        REBOOTcode = False
        try:
            session = {}
            if main(session = session) == "REBOOTcode":
                REBOOTcode = True
        except KeyboardInterrupt:
                pass
        except SystemExit as e:
            if session.get("log"):
                session["log"].add(f"SystemExit : {e.code}", "INFO")
            raise e
        except Exception as e:
                trace = traceback.format_exc()
                print(c.ROUGE[0])
                print("========== ERREUR ==========")
                print("Type :", type(e).__name__)
                print("Message :", str(e))
                print("\n--- Traceback complet ---")
                print(trace, file=sys.stderr)
                print("\n============================")
                print(c.RESET)
                print(_("""Voilà, tu as fait planter Winion ! 🐱‍💻
                        Ne t’inquiète pas, c’est pour ça qu’on a besoin de toi.
                        Dépêche-toi de le signaler sur la page, coche, copie l’erreur et envoie.
                        Et pour t’éviter de remplir tous les détails (OS, version, etc.),  
                        je te donne directement les infos :
                        """))
                print("==> https://forms.gle/J57ndxdC6LmU3XQm9")
                print(_("Système d'exploitation :") + " " + platform.system() + "_" + platform.release() + "_" + platform.machine())
                print(_("Version :") + " " + VERSION.VERSION.version())
                print("Build :" + " " + VERSION.VERSION.build())
                ID = format(zlib.crc32((str(type(e).__name__) + str(trace)).encode()), '08x')
                print("ID error : " + ID)
                print(_("Merci pour ton aide !"))
                with zipfile.ZipFile(f"Crash_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{ID}.zip", "w", compression=zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr("Traceback.txt", f"Type : {type(e).__name__}\nMessage : {str(e)}\n\n--- Traceback complet ---\n{trace}\n")
                    zf.writestr("Trace.json", json.dumps({}, indent=2))
        finally:
            actions = [
                lambda: session["api"].stop(),
                lambda: session["trayservice"].stop(),
                lambda: session["ThreadPool"].shutdown(wait=True),
                lambda: sys.settrace(None),
                lambda: session["TraceInjector"].close(),
                lambda: open('Cache.WCP', "wb").write(session["cache"].close())
                #lambda: upnp.deleteportmapping(51413, "TCP"),
                #lambda: upnp.deleteportmapping(51413, "UDP")
            ]
            
            for action in actions:
                try:
                    action()
                except Exception as e:
                    if session.get("log"):
                        session["log"].add(f"'{action}' -> {e}", "ERROR")
            if session.get("log"):
                session["log"].close()
            
            with open("index", "wb") as f:
                f.write(struct.pack("!B", 0))
            
            if VERSION.VERSION.release() == "DEV":
                print("finally : OK")