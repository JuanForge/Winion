import os
import sys
import polib
import requests
import subprocess
from typing import Union
class Translator:
    def __init__(self, source_lang: str = "auto", target_lang: str = "en"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.session = requests.session()
        self.server = "http://127.0.0.1:5000/translate"
    
    def translate(self, text: Union[str, list], source: str = None, target: str = None):
        if source == None:
            source = self.source_lang
        if target == None:
            target = self.target_lang
        
        #space = nb_espaces = len(text) - len(text.rstrip(' '))
        #print(space)
        payload = {
            "q": text,
            "source": source,
            "target": target,
            # "alternatives": 60,
            "format": "text"
        }
        response = requests.post(self.server, json=payload)
        response.raise_for_status()
        return response.json()["translatedText"]
        #if isinstance(text, list):
class extract:
    def __init__(self):
        pass
    def main(self, path: list, base = os.getcwd()) -> list:
        LISTE = []
        for base_dir in path:
            if os.path.isdir(base_dir):
                for root, dirs, filenames in os.walk(base_dir):
                    for filename in filenames:
                        rel_root = os.path.relpath(root, base)
                        if filename.endswith(".py"):
                            LISTE.append(os.path.join(rel_root, filename))
            else:
                LISTE.append(base_dir)
        return LISTE

sentences = [
    "Hello, how are you today?",
    "The weather is nice but a bit windy.",
    "I love programming in Python.",
    "LibreTranslate works quite well.",
    "Let's test how good your translation is!",
    "She walked quietly through the forest, listening to the sound of the wind.",
    "Artificial intelligence is changing the world faster than ever.",
    "He didn’t know what to say, so he just smiled.",
    "When the system crashed, everyone panicked for a moment.",
    "I haven’t slept much lately, but I’m still feeling productive.",
    "The sun was setting behind the mountains, painting the sky orange.",
    "Learning new languages opens your mind to new ways of thinking.",
    "Sometimes, the hardest part is just getting started.",
    "This tool can translate entire documents automatically.",
    "Don’t forget to save your work before restarting your computer.",
    "A strong coffee in the morning can change your entire day.",
    "They decided to travel without any plans, just following the road.",
    "He tried to fix the bug, but it kept coming back.",
    "Music helps me focus when I’m working late at night.",
    "Technology should serve people, not the other way around.",
    "If you want to go fast, go alone. If you want to go far, go together.",
    "She looked at the ocean and felt completely free.",
    "Even small improvements every day can lead to big results.",
    "It’s not about being perfect; it’s about being consistent.",
    "The translation seems accurate, but the tone feels a bit formal."
] * 4

if __name__ == "__main__":
    import time
    folders = extract().main(["./main.py", "./src", "./Lib"])
    print(folders)
    cmd = [
        sys.executable,
        os.path.join("Tools", "pygettext.py"),
        "-d", "Winion",
        "-o", "Winion.pot"
    ] + folders
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.run(cmd, check=True, env=env)

    for i in ["en", "he", "es"]:
        po = polib.pofile("Winion.pot")
        session = Translator("fr", i)
        for entry in po:
            if entry.msgid.strip() and not entry.translated():
                for file_path, lineno in entry.occurrences:
                    print(f"{os.path.relpath(file_path, os.getcwd())}:{lineno}")
                entry.msgstr = session.translate(entry.msgid)
        
        po.metadata = {"Content-Type": r"text/plain; charset=UTF-8", "language": i.lower()}
        #po.metadata = {}
        # po.save(os.path.join(OutBuild, "Languages", ISOout.lower(), "LC_MESSAGES", "Winion.po"))
        po.save(f"{i}.po")
        # po.save_as_mofile(os.path.join(OutBuild, "./Languages", ISOout.lower(), "LC_MESSAGES", "Winion.mo"))
        po.save_as_mofile(f"{i}.mo")
        

    if True == False:
        session = Translator("fr", "en")
        print(session.translate("Bonjour "))
        print(session.translate(["Bonjour "]))

        start_time = time.perf_counter_ns()
        print(Translator("en", "fr").translate(sentences))
        print(time.perf_counter_ns() - start_time)