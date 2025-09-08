import io
import os
import sys
import time
import pickle
import threading

from pympler import asizeof
from functools import wraps
from typing import Optional, Union, IO
from datetime import datetime, timezone
from collections.abc import Mapping, Container

from Lib import Debug
from Lib.BlackHoles import BlackHoles

class errors:
    class InvalidSignature(Exception):
        pass
    class invalid:
        class Signature:            
            class SessionInvalide(Exception):
                pass
            
            class CachePlein(Exception):
                pass


class session:
    __version__ = "0.00.2"
    __build__ = "2025.09.08:21.16"
    def __init__(self, sessionLog: Debug.log.session = BlackHoles(), MaxSize = 512 * 1024 * 1024, threaded: bool = False, header: str = __version__):
        """
        threaded bool
            Active un thread dédié à la gestion du cache.
        
            Cela permet une optimisation importante des performances, car 
        
            - Chaque appel à `set()` est allégé, il ne gère plus les indexations, suppressions ou vidages.
            - Toutes les opérations de maintenance (tri, nettoyage, vidage) sont déléguées au thread de fond.
            - Permet de ne pas bloquer le thread principal, même sur de très gros caches.
        """
        self.cache = {"def": {}, "wrapper": {}}
        self.log = sessionLog
        self.MaxSize = MaxSize
        self.lock = threading.Lock()
        self.threaded = threaded
        self.HEADER = header
        self._stop_event = threading.Event()
        
        if threaded:
            self._thread = threading.Thread(target=self._threadloop, name="Cache")
            self._thread.start()
    
    def _threadloop(self):
        while not self._stop_event.is_set():
            self._clear()
            time.sleep(20)
    
    
    def load(self, source: IO[bytes]):
        if source.read(len(self.HEADER.encode("utf-8"))) == self.HEADER.encode("utf-8"):
            self.cache = pickle.load(source)
        else:
            raise errors.InvalidSignature("InvalidSignature")
    
    
    def close(self) -> bytes:
        if self.threaded:
            self._stop_event.set()
            self._thread.join()
        buffer = io.BytesIO()
        buffer.write(self.HEADER.encode('utf-8'))
        pickle.dump(self.cache, buffer, protocol=pickle.HIGHEST_PROTOCOL)
        return buffer.getvalue()
    
    
    def _clear(self,):
        while self.getsize() > self.MaxSize:
            print(f"Cache size = {self.getsize()} > MaxSize = {self.MaxSize}")
            oldest_key = None
            oldest_date = None
            
            def find_oldest(d, path=()):
                nonlocal oldest_key, oldest_date
                for k, v in d.items():
                    if isinstance(v, dict) and 'date' in v and 'value' in v:
                        try:
                            d_date = datetime.fromisoformat(v['date'])
                        except Exception:
                            d_date = datetime.max
                        if oldest_date is None or d_date < oldest_date:
                            oldest_date = d_date
                            oldest_key = path + (k,)
                    elif isinstance(v, dict):
                        find_oldest(v, path + (k,))
            
            find_oldest(self.cache)
            
            if oldest_key is None:
                break
            
            self.set(oldest_key, False)
            self.log.add(f"Cache taille dépassée, suppression de la clé la plus ancienne : {oldest_key}", level='DEBUG')
    
    def set(self, key, value):
        """
        ---- 🇫🇷 Français ----
        
        Arguments :
        - key : définit l'emplacement virtuel où sera stocké le contenu.  
        - - Exemple : `session.set(('variable', 'str', '0x01'), 'Bonjour')`
        - value : la valeur à stocker (tout type est accepté : int, str, float, fonction, etc.)
        
        🗑️ Si la valeur passée (`value`) est `False`, la clé est entièrement supprimée, y compris son contenu et tous ses index associés.
        
        ---- 🇺🇸 English ----
        
        Arguments :
        - key: defines the virtual location where the content will be stored.  
        - - Example: `session.set(('variable', 'str', '0x01'), 'Bonjour')`
        - value: the value to store (any type is accepted: int, str, float, function, etc.)
        
        🗑️ If the value provided (`value`) is `False`, the key will be completely removed, including its content and all associated indexes.
        """
        
        date = datetime.now(timezone.utc)
        stored_data = {'value': value, 'date': date}
        if isinstance(key, tuple):
            current = self.cache["def"]
            for subkey in key[:-1]:
                if subkey not in current:
                    current[subkey] = {}
                current = current[subkey]
            current[key[-1]] = stored_data
        else:
            self.cache["def"][key] = stored_data
        
            self.log.add(f'{key} SET {value}', level='DEBUG')
        
        if self.threaded == False:
            self._clear()
    
    
    def get(self, key, ignoreFalse=False):
        if isinstance(key, tuple):
            current = self.cache["def"]
            for subkey in key:
                if isinstance(current, dict) and subkey in current:
                    current = current[subkey]
                else:
                    current = None
                    break
            if current:
                retourn = current['value']
            else:
                retourn = None
            
            if self.log:
                self.log.add(f'{key} GET {retourn}', level='DEBUG')
        else:
            retourn = self.cache["def"].get(key, None)
            if retourn:
                retourn = retourn['value']
            if self.log:
                self.log.add(f'{key} GET {retourn}', level='DEBUG')
        return retourn
    
    
    def wrapper(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            #if isinstance(func, (staticmethod, classmethod)):
            #    real_func = func.__func__
            real_func = getattr(func, '__func__', func)
            key = (real_func.__module__, real_func.__qualname__, real_func.__code__.co_filename, real_func.__code__.co_firstlineno, args, tuple(sorted(kwargs.items())))
            #print(key)
            with self.lock:
                if key in self.cache["wrapper"]:
                    self.log.add(f"Cache hit for {real_func.__qualname__} with key {key}", level="DEBUG")
                    return self.cache["wrapper"][key]['value']
            
            result = real_func(*args, **kwargs)
            with self.lock:
                self.cache["wrapper"][key] = {'value': result, 'date': datetime.now(timezone.utc)}
                self.log.add(f"Cache set for {real_func.__qualname__} with key {key}", level="DEBUG")
            return result
        return wrapped
    
    def _deep_getsizeof(self, obj, seen=None): # REMPLACER PAR MemorySize
        if seen is None:
            seen = set()
    
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        
        seen.add(obj_id)
        size = sys.getsizeof(obj)
        
        if isinstance(obj, dict):
            size += sum(self._deep_getsizeof(k, seen) + self._deep_getsizeof(v, seen) for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set, frozenset)):
            size += sum(self._deep_getsizeof(i, seen) for i in obj)
        elif isinstance(obj, Container) and not isinstance(obj, (str, bytes, bytearray)):
            try:
                size += sum(self._deep_getsizeof(i, seen) for i in obj)
            except Exception:
                pass
        return size
    def getsize(self):
        return self._deep_getsizeof(self.cache)
    
    def MemorySize(self):
        return asizeof.asizeof(self.cache)
