import sys
import locale
import gettext

iso = locale.getlocale()[0].split("_")[0] #! Exprès pour faire planter les Python qui ne donnent pas ce qu’il faut.
try:
    iso = locale.getlocale()[0].split("_")[0]
except Exception:
    iso = None

if iso:
    tr = gettext.translation("Winion", localedir="./Languages", languages=["default", iso, "en"], fallback=True)
    _ = tr.gettext
    LANG = tr.info().get("language", None)
else:
    _ = lambda x: x
