#TRANSPORT \\ file: Path = None
import os
import json
import inspect
import threading

from typing import IO
from typing import Tuple
from pathlib import Path
from typing import Literal
from datetime import datetime, timezone

class level:
    _lv0DEBUG_ = ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    _lv1INFO_ = ('INFO', 'WARNING', 'ERROR', 'CRITICAL')
    _lv2WARNING_ = ('WARNING', 'ERROR', 'CRITICAL')
    _lv3ERROR_ = ('ERROR', 'CRITICAL')
    _lv4CRITICAL_ = ['CRITICAL']

class session:
    def __init__(self, out: IO[str],
            level: list = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            showStackTrace: bool = True,
            prefix: str = None,
            enablePrint: bool = False,
            flush: bool = False,
            byint: int = 50):
        self.showStackTrace = showStackTrace
        self.out = out
        self.requitLevel = level
        self.prefix = prefix
        self.enablePrint = enablePrint
        self._lock = threading.Lock()
        self._flush = flush
        self.byint = byint
    
    def _FIX(self, s: str, taille=8) -> str:
        if len(str(s)) > taille:
            return str(s)[:taille]
        return str(s).ljust(taille)
    
    def _emoji(self, data: str) -> str:
        entry = {"DEBUG": "[🔍] DEBUG",
                "INFO": "[📢] INFO",
                "WARNING": "[⚠️] WARNING",
                "ERROR": "[🔴] ERROR",
                "CRITICAL": "[☠️] CRITICAL"}
        return entry.get(data, data)
    
    
    def flush(self):
        self.out.flush()
    
    
    def add(self, entry: str, level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'DEBUG') -> bool:
        if not level in self.requitLevel:
            return None
        """
        stack = inspect.stack()
        caller = stack[1]
        
        fn_name = caller.function
        lineno = caller.lineno
        filename = os.path.basename(caller.filename)
        
        cls_name = None
        frm = caller.frame
        if 'self' in frm.f_locals:
            cls_name = frm.f_locals['self'].__class__.__name__
        elif 'cls' in frm.f_locals:
            cls_name = frm.f_locals['cls'].__name__
        
        if cls_name:
            by = f"{cls_name}.{fn_name}"
        else:
            by = fn_name
        """
        
        stack = inspect.stack()
        caller = stack[1]
        
        fn_name = caller.function
        lineno = caller.lineno
        filename = os.path.basename(caller.filename)
        frm = caller.frame
        
        cls_name = None
        if 'self' in frm.f_locals:
            cls = frm.f_locals['self'].__class__
            cls_name = cls.__module__ + '.' + cls.__qualname__
        elif 'cls' in frm.f_locals:
            cls = frm.f_locals['cls']
            cls_name = cls.__module__ + '.' + cls.__qualname__
        
        if cls_name:
            by = f"{cls_name}.{fn_name}"
        else:
            by = fn_name
        
        entry = {
            "level": str(level),
            "timeISO": datetime.now(timezone.utc).isoformat(),
            "timeLocal": datetime.now().isoformat(),
            "log": str(entry),
            "prefix": str(self.prefix),
            "StackTrace": f"{filename}:{lineno}",
            "by": str(by)
        }
        
        data = f"{entry['timeLocal']} : [{self._FIX(entry['prefix'], 10)}] > [{self._FIX(self._emoji(entry['level']), 12)}] {self._FIX(entry['StackTrace'], 20)}:[{self._FIX(entry['by'], self.byint)}] >> {entry['log']}"
        with self._lock:
            self.out.write(data + "\n")
            if self._flush:
                self.out.flush()
            
            if self.enablePrint:
                print(data)
        
        
    def close(self, outclose: bool = True) -> None:
        self.out.close()
        return None