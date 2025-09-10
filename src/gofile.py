import time
import requests
from Lib import Debug
from Lib.BlackHoles import BlackHoles

class gofile:
    @staticmethod
    def headers():
        headers = {"User-Agent": "Mozilla/5.0","Accept-Encoding": "gzip, deflate, br","Connection": "keep-alive"}
        return headers
    
    @staticmethod
    def get_token(log: Debug.log.session = BlackHoles()):
        try:
            response = requests.post("https://api.gofile.io/accounts", headers=gofile.headers()).json()
        except Exception as e:
            log.add(f"F.gofile.get_token : ERREUR de requests : {e}", "ERROR")
            return False
        if not response["status"] == "ok":
            log.add("F.gofile.get_token : Erreur lors de la création du compte !", "ERROR")
            return False
        else:
            log.add(f"token recus : " + response["data"]["token"])
            return response["data"]["token"]
    
    @staticmethod
    def get_files_info(content_id, token, log: Debug.log.session = BlackHoles()):
        log.add(f"content_id={content_id}, token={token}")
        url = f"https://api.gofile.io/contents/{content_id}?wt=4fd6sg89d7s6&cache=true"
        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers).json()
        except Exception as e:
            log.add(f"ERREUR de requests : {e}", "ERROR")
            return False
        
        if not response["status"] == "ok":
            log.add(f"Erreur lors de la récupération du contenu: {url}")
            return False
        
        data = response["data"]
        files_info = {}
        if data["type"] == "folder":
            for child in data["children"]:
                child_data = data["children"][child]
                if child_data["type"] == "folder":
                    files_info.update(gofile.get_files_info(child_data["id"], token))
                else:
                    files_info[child_data["id"]] = {
                        "filename": child_data["name"],
                        "link": child_data["link"]
                    }
        else:
            files_info[content_id] = {
                "filename": data["name"],
                "link": data["link"]
            }
        log.add(f"return : {files_info}")
        return files_info
    
    @staticmethod
    def get(url, password='', log: Debug.log.session = BlackHoles()):
        log.add(f"F.gofile.get : url={url}")
        content_id = url.split("/")[-1]
        
        token = gofile.get_token()
        if not token:
            log.add("ERREUR : aucun token n'a est-ai donner par ' gofile.get_token() '", "ERROR")
            return False, None
        
        files_info = gofile.get_files_info(content_id, token)
        if not files_info:
            log.add(f"F.gofile.get : ERREUR : Aucun fichier trouvé pour {url}.")
            return False, None
        for file_info in files_info.values():
            #print(file_info)
            #print(file_info['filename'] + ' : ' + file_info['link'])
            headers = {"Authorization": f"Bearer {token}"}
            return file_info['link'], headers