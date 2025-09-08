import py7zr
""""
import py7zr        // MARCHE PAS POUR LES ARCHIVE LV.9
        with py7zr.SevenZipFile(fichier, mode='r') as archive:
            archive.extractall(path=output)

import libarchive   // QUE UNIX
"""
import os
import magic
import zipfile
import subprocess

from pathlib import Path
from typing import Optional


from Lib import Debug
from Lib.BlackHoles import BlackHoles

class errors:
    class NotFound7zip(Exception): pass
    class NotFoundArchive(Exception): pass
    class UnknownFormatArchive(Exception): pass

class Archive:
    @staticmethod
    def type(fichier: str, log: Debug.log.session = BlackHoles()) -> str:
        log.add(f"fichier={fichier}")
        
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(fichier)
        
        if "zip" in file_type:
            log.add("Return 'zip'")
            return 'zip'
        
        elif "x-7z-compressed" in file_type:
            log.add("Return '7z'")
            return '7z'
        
        else:
            log.add(f"Type de fichier non identifié : {file_type}", "ERROR")
            raise errors.UnknownFormatArchive(f"Type de fichier non identifié : {file_type}")
    
    """
    def unzip(fichier, output):
        Log.add(f"F.unzip : fichier={fichier}, output={output}", echo=False)
        with py7zr.SevenZipFile(fichier, mode='r') as archive:
            archive.extractall(path=output)
        return True
    """
    @staticmethod
    def unzip(fichier: str, output: str, log: Debug.log.session = BlackHoles()):
        log.add(f"fichier={fichier}, output={output}")

        os.makedirs(output, exist_ok=True)
        
        result = subprocess.run(f'call "Bin\\7zip\\7z.exe" x "{fichier}" -o"{output}" -mmt=on -bb -y', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        if result.returncode == 0:
            log.add(f"Décompression OK")
            return True
        else:
            if not os.path.isfile(fichier):
                raise errors.NotFoundArchive()
            
            elif not os.path.isfile("Bin\\7zip\\7z.exe"):
                raise errors.NotFound7zip()
            
            else:
                log.add(f"ERREUR : {result.stdout}, = {result.returncode}", level='ERROR')
            return False

    """
    @staticmethod
    def test(fichier, log: Optional[log._session] = BlackHoles()):
        log.add(f"fichier={fichier}")
        if not os.path.isfile(fichier):
            log.add(f"404 Archive : {fichier}", level='ERROR')
            return False
        format = Archive.type(fichier)
        try:
            if format == "7z":
                with py7zr.SevenZipFile(fichier, mode='r') as archive:
                    if archive.test() is None:
                        log.add("Archive OK")
                        return True
                    else:
                        log.add("Archive Corrompue", level='WARNING')
                        return False

            elif format == "zip":
                with zipfile.ZipFile(fichier, mode='r') as archive:
                    if archive.testzip() is None:
                        log.add("Archive OK")
                        return True
                    else:
                        log.add("Archive Corrompue", level='WARNING')
                        return False

        except Exception as e:
            log.add(f"ERREUR : {e}", level='ERROR')
            return False
    """