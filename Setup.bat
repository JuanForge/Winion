@echo off
chcp 65001 >nul
CD /D %~dp0
set GUI=false
for %%a in (%*) do (
    if "%%a"=="--install-GUI" set GUI=true
)
echo [*] GUI : %GUI%
echo [*] Vérification de l'environnement Python...
set "argPip=--no-cache-dir --no-user --no-input"
if exist ".\.Embeded\python.exe" (
    echo [*] Installation des dépendances depuis requirements.txt...
    call ".\.Embeded\python.exe" -m pip install wheel %argPip%
    call ".\.Embeded\python.exe" -m pip install --upgrade pip %argPip%
    if "%GUI%" == "true" (
        call ".\.Embeded\python.exe" -m pip install -r ".\requirementsGUI.txt" %argPip%
    )
    call ".\.Embeded\python.exe" -m pip install -r ".\requirements.txt" %argPip%
    if %errorlevel% == 0 (
        echo [OK] Installation terminée.
        if exist ./Main.pyc (
            call ".\.Embeded\python.exe" Main.pyc --boot
        ) else (
            call ".\.Embeded\python.exe" Main.py --boot
        )
        pause
        exit /b 0
    ) else (
        echo [ERROR] ERREUR DE PIP
        pause
        exit /b 14
    )
) else (
    echo [ERROR] Python est introuvable.
    pause
    exit /b 19
)