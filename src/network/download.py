import time
import requests
import textwrap
import threading
import traceback

from tqdm import tqdm
from typing import Union, Optional, Iterator


from Lib import Debug
from Lib.BlackHoles import  BlackHoles


from src.gofile import gofile
from src.colorV2 import color as c
from src.LinkManager import link2direct

class errors:
    class FailedRequest(Exception): pass
    class InvalideHTTP(Exception): pass

def download(url: str,
            requestsSession: requests.Session = requests.Session(),
            chunkSize: int = 8192,
            log: Debug.log.session = BlackHoles(),
            speedNetwork: Union[int, float] = 1024 * 1024 * 1024 * 1024 * 1024,
            prefix="",
            leave=False,
            bar_size=None, #120
            Use_Exception_for_error=False,
            headers: dict = None,
            AllowRedirects: bool = True) -> Iterator[bytes]:
    try:
        response = requestsSession.get(url, stream=True, headers=headers, allow_redirects=AllowRedirects)
        if response.status_code == 200:
            total_size = int(response.headers.get('Content-Length', 0))
            
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024,
                    bar_format=prefix + "{desc}|{bar}| {n_fmt}/{total_fmt} [{rate_fmt}]", 
                    mininterval=0.8, leave=leave, ncols=bar_size, dynamic_ncols=True) as bar:
                
                for chunk in response.iter_content(chunk_size=chunkSize):
                    start_time = time.time()
                    if not chunk:
                        break
                    
                    yield chunk
                    
                    bar.update(len(chunk))
                    
                    expected_time = len(chunk) / speedNetwork
                    elapsed_time = time.time() - start_time
                    
                    if elapsed_time < expected_time:
                        time.sleep(expected_time - elapsed_time)
            return True
        else:
            log.add(f"{url} > HTTP:{response.status_code}", "ERROR")
            message_en_fin = '| 0M/0MB (ERROR http)'
            if not bar_size:
                bar_size = 120
            bar_size -= (len(prefix) + len(message_en_fin))
            print(f'{prefix}|', end='')
            for i in range(bar_size - 1):
                print(f"{c.ROUGE[0]}█{c.RESET}", end='')
            print(message_en_fin)
            raise errors.InvalideHTTP()
    except Exception as e:
        text = textwrap.dedent(f"""\
            ========== ERREUR ==========
            Type : {type(e).__name__}
        
            Message : {str(e)}
        
            --- Traceback complet ---
            {traceback.format_exc()}
            ============================
            """)
        log.add(text, "ERROR")
        
        message_en_fin = '| 0M/0MB (ERREUR interne)'
        bar_size -= (len(prefix) + len(message_en_fin))
        print(f'{prefix}|', end='')
        for i in range(bar_size - 1):
            print(f"{c.ROUGE[0]}█{c.RESET}", end='')
        print(message_en_fin)
        log.add(f"Erreur de téléchargement: {e}", "ERROR")
        raise errors.FailedRequest()