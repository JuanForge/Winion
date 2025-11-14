import sys
import locale
import gettext
import threading

iso = locale.getlocale()[0].split("_")[0] #! Exprès pour faire planter les Python qui ne donnent pas ce qu’il faut.
try:
    iso = locale.getlocale()[0].split("_")[0]
except Exception:
    iso = None
"""
if iso:
    tr = gettext.translation("Winion", localedir="./Languages", languages=["default", iso, "en"], fallback=True)
    _ = tr.gettext
    LANG = tr.info().get("language", None)
else:
    _ = lambda x: x
"""
_lock = threading.Lock()

class I18N:
    __slots__ = ("translate", "lang")
    def __init__(self, translate, lang):
        self.translate = translate
        self.lang = lang

_CURRENT = I18N(lambda x: x, "en")


def _update():
    global _CURRENT

    with _lock:
        print(iso)
        if iso:
            tr = gettext.translation(
                "Winion",
                localedir="./Languages",
                languages=["default", iso, "en"],
                fallback=True
            )
            new_obj = I18N(tr.gettext, tr.info().get("language", None))
        else:
            new_obj = I18N(lambda x: x, None)
        
        _CURRENT = new_obj
_update()

def _(s: str) -> str:
    return _CURRENT.translate(s)
