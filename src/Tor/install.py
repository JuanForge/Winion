import io
import tarfile
import requests


from typing import Optional


from Lib import Debug
from Lib.BlackHoles import  BlackHoles


from src.network import download


def install(log: Debug.log.session = BlackHoles()) -> bool:
    buffer = io.BytesIO()
    for chunk in download('https://archive.torproject.org/tor-package-archive/torbrowser/14.5.1/tor-expert-bundle-windows-x86_64-14.5.1.tar.gz',
                            requestsSession=requests.Session(),
                            log=log,
                            prefix="File:Tor",
                            speedNetwork=1.5 * 1024 * 1024,
                            leave=True):
        buffer.write(chunk)
    
    buffer.seek(0)
    
    try:
        with tarfile.open(fileobj=buffer, mode='r:gz') as archive:
            archive.extractall(path='Bin/Tor')
        return True
    except tarfile.TarError as e:
        log.add(f"[Tor] Erreur d'extraction : {e}", "ERROR")
        return False