Prototype = True

import io
import os
import sys
import json
import time
import zlib
import ctypes
import datetime
import platform
import linecache
import threading
import sysconfig


from typing import IO
from typing import Optional

PyFrame_LocalsToFast = ctypes.pythonapi.PyFrame_LocalsToFast
PyFrame_LocalsToFast.argtypes = [ctypes.py_object, ctypes.c_int]
PyFrame_LocalsToFast.restype = None




stdlib_dir = sysconfig.get_paths()["stdlib"]
hooks = {
    "0x6edfb439_": lambda frame: frame.f_locals.update({"a": 5}), #! DEV
    "0x5363ef09_": lambda frame: print("Ligne interceptée"), #! DEV
}

PROJECT_ROOT = os.path.abspath(os.getcwd())

class session:
    def __init__(self, out: IO[str], TypeJSON = None, addExecute = False,
                 addFilename = True, addCodeObject = False,
                 exclude_stdlib = True, addLocalsState = True, addGlobalsState = False):
        self.TypeJSON = TypeJSON
        self.addExecute = addExecute
        self.addFilename = addFilename
        self.addCodeObject = addCodeObject
        self.addLocalsState = addLocalsState
        self.addGlobalsState = addGlobalsState
        
        self.exclude_stdlib = exclude_stdlib
        
        self.out = out
        #self.out = io.StringIO()
        
        self.out.write("[\n")
        self.out.write(json.dumps({
                                    "pid": os.getpid(),
                                    "python_version": platform.python_version(),
                                    "platform": platform.platform(),
                                    "executable": sys.executable,
                                    "cwd": os.getcwd(),
                                    "started": datetime.datetime.now().isoformat(),
                                    "entry": []
                                }, indent=4)[:-3] + "\n")
        
        self._unit = 0
        self._lasttime = time.perf_counter_ns()
        self._lastentry = {}
        self.lock = threading.Lock()
    
    def _space(self, entry: str, num: int):
                return '\n'.join(num * ' ' + line for line in entry.splitlines())
    
    def safe_json_obj(self, obj, _depth=0):
        if _depth > 5:
            return "<too-deep>"
    
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        elif isinstance(obj, (list, tuple, set)):
            return [self.safe_json_obj(i, _depth + 1) for i in obj]
        elif isinstance(obj, dict):
            return {
                str(self.safe_json_obj(k, _depth + 1)): self.safe_json_obj(v, _depth + 1)
                for k, v in obj.items()
            }
        else:
            return f"<non-serializable: {type(obj).__name__}>"
    
    def close(self):
        entry = self._lastentry
        entry['timeExe'] = time.perf_counter_ns() - self._lasttime
        self.out.write(",\n" + self._space(json.dumps(entry, indent=self.TypeJSON), 4) + "\n")
        self.out.write("  ]" + "\n" + "}")
        self.out.write("\n]\n")
        self.out.close()
    
    def tracer(self, frame, event, arg):
        code = frame.f_code
        filename = code.co_filename
        if not PROJECT_ROOT in filename:
            return self.tracer
        timeExe = time.perf_counter_ns() - self._lasttime
        func_name = code.co_name
        lineno = frame.f_lineno
        #if self.exclude_stdlib == True and os.path.dirname(os.__file__) in filename:
        #    return self.tracer
        #
        
        with self.lock:
            unique_str = f"{func_name} {filename} {lineno}"
            crc = zlib.crc32(unique_str.encode('utf-8'))
            crc_hex = f"0x{crc:08x}"
            if not self._unit == 0:
                entry = self._lastentry
                entry['timeExe'] = timeExe
            self._lastentry = {
                                "address": crc_hex,
                                "event":  event,
                                "num": self._unit,
                                "thread_id": threading.get_ident(),
                                "thread_name": threading.current_thread().name,
                                "timeExe": timeExe,
                                "func_name": func_name,
                                "lineno": lineno,
                                "arg": self.safe_json_obj(arg)
                            }
            if self.addExecute:
                self._lastentry["execute"] = linecache.getline(filename, lineno).strip()
            if self.addFilename:
                self._lastentry["filename"] = filename
            if self.addCodeObject:
                self._lastentry["CodeObject"] = str(code)
            
            
            if self.addLocalsState:
                self._lastentry["localsState"] = self.safe_json_obj(frame.f_locals)
            if self.addGlobalsState:
                self._lastentry["globalsState"] = self.safe_json_obj(frame.f_globals)
            
            
            # Dump locals
            if not self._unit == 1:
                data = ",\n"
            else:
                data = ""
            
            if not self._unit == 0:
                json_text = json.dumps(entry, indent=self.TypeJSON)
                indented_json_text = '\n'.join(8 * ' ' + line for line in json_text.splitlines())
                self.out.write(data + indented_json_text)
                #self.out.write(data + json.dumps(entry,
                #                           indent=4,
                #                           default=str))
            self._unit += 1 
            
            if event == 'call':
                1 + 1
                #print(f"[ {crc_hex} ] > [CALL] {func_name} ({filename}:{lineno})")
            
            elif event == 'line':
                #print(f"[ {crc_hex} ] > [LINE] {filename}:{lineno} - {line}")
                
                if crc_hex == "0xb1a86a50":
                    """#! DEV"""
                    #print(f">>> Injection : modification de 'a' dans {func_name} à 5")
                    time.sleep(1)
                    frame.f_locals['a'] = 5
                    PyFrame_LocalsToFast(frame, 1)
            
            #elif event == 'return':
            #    print(f"[ {crc_hex} ] > [RETURN] → {arg}")
            
            if crc_hex in hooks:
                hooks[crc_hex](frame)
                PyFrame_LocalsToFast(frame, 1)
            self._lasttime = time.perf_counter_ns()
            return self.tracer