import os
import sys
import time
import signal
import pystray
import platform
import threading


from PIL import Image, ImageDraw
from pystray import Menu, MenuItem


from Lib import Cache


from src.i18n import _

if platform.system() == "Windows":
    import ctypes
    import win32console # type: ignore
    console_hwnd = win32console.GetConsoleWindow()

console_visible = True
etat_debug = {'on': False} #! test #add

class trayservice:
    class session:
        def __init__(self, cache = Cache.session, STOP: dict = [False]):
            self.console_visible = True
            self.etat_debug = {'on': False}
            self.icon = None
            self.cache = cache
            self.STOP = STOP
        
            self.icon = pystray.Icon(
                'Winion',
                icon=self._loadIcon(),
                title='Winion'
            )
        
            self.icon.menu = Menu(
                MenuItem(_('Afficher / Masquer Console'), self.toggle_console, default=True),
                MenuItem(_('Action 1'), self.action1),
                MenuItem(_('Action 2'), self.action2),
                Menu.SEPARATOR,
                MenuItem(
                    _('Mode Debug'),
                    self.toggle_debug,
                    checked=lambda item: self.etat_debug['on']
                ),
                Menu.SEPARATOR,
                MenuItem(_('Quitter'), self.quit_app)
            )
        
        def _loadIcon(self):
            with self.cache.lock:
                data = self.cache.get(("trayservice", "ICO"))
                if not data:
                    data = Image.open("./Assets/icon.ico").copy() #! Partie instable
                    self.cache.set(("trayservice", "ICO"), data)
                return data
        
        
        def hide_console(self):
            if platform.system() == "Windows":
                ctypes.windll.user32.ShowWindow(console_hwnd, 0)
            else:
                print(_("[Info] Cacher la console n'est pas supporté sous votre OS."))
        
        def show_console(self):
            if platform.system() == "Windows":
                ctypes.windll.user32.ShowWindow(console_hwnd, 1)
            else:
                print(_("[Info] Afficher la console n'est pas supporté sous votre OS."))
        
        def toggle_console(self, icon=None, item=None):
            if self.console_visible:
                self.hide_console()
            else:
                self.show_console()
            self.console_visible = not self.console_visible
            return True
        
        def toggle_debug(self, icon, item):
            self.etat_debug['on'] = not self.etat_debug['on']
            print(_(f"Mode debug {'activé' if self.etat_debug['on'] else 'désactivé'}"))
            icon.update_menu()
            return True
        
        def action1(self, icon, item):
            print(_("Action 1 exécutée"))
            return True
        
        def action2(self, icon, item):
            print(_("Action 2 exécutée"))
            return True
        
        def quit_app(self, icon, item):
            print(_("Fermeture du programme"))
            self.STOP[0] = True
            signal.raise_signal(signal.SIGINT)
            #sys.exit(0) #! marche que dans le Main-Thread donc de la merde
        
        def Execute(self):
            self.icon.run()
        def stop(self):
            self.icon.stop()