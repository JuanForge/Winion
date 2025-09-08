Prototype = True


import re
import json
import socket


from src.VERSION import VERSION

class settings:
    class errors:
        class SettingsError(Exception):
            pass

        class KeyUnknown(SettingsError):
            def __init__(self, key):
                super().__init__(f"[settings] Clé inconnue : '{key}'")

    @staticmethod
    def load():
        with open("settings.json", 'r') as file:
            data = json.load(file)
            return settings._safe_replace(data)

    @staticmethod
    def _key(key: str) -> str:
        if key == 'localIP':
            return socket.gethostbyname(socket.gethostname())
        
        elif key == 'version':
            return VERSION.version()
        
        elif key == 'build':
            return VERSION.build()
        
        elif key == 'ReleaseType':
            VERSION.release()

        else:
            raise settings.errors.KeyUnknown(key)

    def _safe_replace(data):
        if isinstance(data, dict):
            result = {}
            for k, v in data.items():
                result[k] = settings._safe_replace(v)
            return result
    
        elif isinstance(data, list):
            result = []
            for item in data:
                result.append(settings._safe_replace(item))
            return result
    
        elif isinstance(data, str):
            matches = re.findall(r"{([^}]+)}", data)
            for key in matches:
                    value = settings._key(key)
                    data = data.replace(f"{{{key}}}", str(value))
            return data
    
        return data