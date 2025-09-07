set APIpython=./Lib
if exist Main.pyc (
    call .Embeded\python.exe Main.pyc
) else (
    call .Embeded\python.exe Main.py
)