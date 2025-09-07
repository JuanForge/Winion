@echo off
setlocal enabledelayedexpansion
set "dossier=%~dp0\.."
set "PATH=%PATH_Winion%;%PATH%"
setx PATH_Winion "%PATH_Winion%" >nul 2>&1
:: METS A JOURS POUR TOUS LES SHELL


:: ----------------------------------------BUILDER----------------------------------------
set "build_cpp=llvm-mingw-full"
set "ARC=%PROCESSOR_ARCHITECTURE%"

set "DEBUG=-w -Qn"
:::: -Wall -Wextra = True
:::: -w -Qn = False
:::: -Wall : Avertissements de base (les plus courants et critiques).
:::: -Wextra : Avertissements supplémentaires et plus détaillés, donc plus verbeux.

set "SecteursFonctions=-ffunction-sections"
::::-ffunction-sections : Divise chaque fonction en une section séparée, ce qui permet de mieux contrôler et d'optimiser l'édition des liens pour éliminer les fonctions inutilisées.
set "SecteursDonnees=-fdata-sections"
::::-fdata-sections place chaque variable dans sa propre section, ce qui permet d'optimiser l'édition des liens en supprimant les données inutilisées.
set "Secteurs=%SecteursFonctions% %SecteursDonnees%"

set "Optimisation=-O3"
::::-O0 : Aucune optimisation. Le code est compilé de manière directe, sans optimisation, ce qui facilite le débogage.
::::-O1 : Optimisation minimale. Applique des optimisations de base, mais sans augmenter les temps de compilation ou rendre le débogage plus difficile.
::::-O2 : Optimisation plus agressive. Active davantage d'optimisations sans sacrifier la stabilité ou la taille du code. C'est généralement le niveau d'optimisation recommandé pour les applications de production.
::::-O3 : Optimisation maximale. Applique des optimisations plus agressives, y compris celles qui peuvent augmenter la taille du code pour obtenir des performances accrues.

set "include_H="
for /r "%dossier%\Builder\H" %%i in (*.ini) do (
    for /f "delims=" %%l in ('type "%%i"') do (
        set "include_H=-I^"%dossier%\%%l^" !include_H!"
    )
)

set "include_Lib="
for /r "%dossier%\Builder\Lib" %%i in (*.ini) do (
    for /f "delims=" %%l in ('type "%%i"') do (
        set "include_Lib=-L^"%dossier%\%%l^" !include_Lib!"
    )
)
set "include=%include_H% %include_Lib%"

set "c2o=%DEBUG% %Optimisation% %Secteurs%"
set "o2dll=%DEBUG% %Optimisation%"
set "build_dll="
set "build_exe=%DEBUG% %Optimisation% -Wl,--gc-sections"
::::-Wl,--gc-sections supprime les connexion inutiliser

::::echo [BIOS] SET : OK
::::echo [BIOS] commande : START
set "dossier="