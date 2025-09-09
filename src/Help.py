from .color import *
from src.i18n import _

def Help_Commande():
  data = ROUGE[0] + f"""

  //SUPPORT//

 help = {_("aide")}

 support = {_("support en ligne")}
""" + VERT + f"""
      ooo        ooooo   .oooooo.   oooooooooo.   ooooo     ooo ooooo        oooooooooooo
      `88.       .888'  d8P'  `Y8b  `888'   `Y8b  `888'     `8' `888'        `888'     `8
       888b     d'888  888      888  888      888  888       8   888          888
       8 Y88. .P  888  888      888  888      888  888       8   888          888oooo8
       8  `888'   888  888      888  888      888  888       8   888          888    "
       8    Y     888  `88b    d88'  888     d88'  `88.    .8'   888       o  888       o
      o8o        o888o  `Y8bood8P'  o888bood8P'      `YbodP'    o888ooooood8 o888ooooood8

apt = {_("Gestionnaire de paquets")}
apt install <module>     =   {_("Installer un/des paquet(s) (Automatisation avec -y) (Pour mettre une version specifique : <module>==<version>)")}
apt remove <module>      =   {_("Supprimer un/des paquet(s)")}
{ORANGE}NEW : apt update =   {_("Met à jour les fichiers d’index des dépôts pour obtenir les dernières informations sur les paquets.")} {VERT}
apt upgrade              =   {_("Mets a jour les paquets")}
check integrity          =   {_("Test complet sur l'entièreté des paquet (Trouver la moindre erreur)")}
{ORANGE}NEW : apt install --CLI  =   {_("Proposse tous les paquets a installable le tous en une interface CLI.")} {VERT}
{ORANGE}NEW : apt get-source     =   {_("Affiche tous les paquets disponible de maniere brute.")} {VERT}

      ooooooooo.         .o.       ooooooooooooo ooooo   ooooo
      `888   `Y88.      .888.      8'   888   `8 `888'   `888'
       888   .d88'     .8"888.          888       888     888
       888ooo88P'     .8' `888.         888       888ooooo888
       888           .88ooo8888.        888       888     888
       888          .8'     `888.       888       888     888
      o888o        o88o     o8888o     o888o     o888o   o888o

DEF : {_("Le PATH sur Windows est une variable d'environnement qui indique où chercher les programmes à exécuter.")}

PATH:<option>
PATH:RESET            =  {_("Réinitialisation (fortement instable)")}
PATH:ADD <dossier>    =  {_("Ajouter un dossier a la recherche")}

        .oooooo.    .oooooo..o
       d8P'  `Y8b  d8P'    `Y8
      888      888 Y88bo.
      888      888  `"Y8888o.
      888      888      `"Y88b
      `88b    d88' oo     .d8P
       `Y8bood8P'  8""88888P'

DEF : {_("Permet d'exécuter des commandes dans le shell du système (Windows = CMD, UNIX = Bash) en utilisant un script dédié (Bin shell.bat).")}
EXEMPLE :
  {_("OS:cmd = lance le CMD")}

  
  .oooooo.     .oooooo.   ooo        ooooo oooooooooo.  ooooo ooooo      ooo       .o.       ooooo  .oooooo..o   .oooooo.   ooooo      ooo
 d8P'  `Y8b   d8P'  `Y8b  `88.       .888' `888'   `Y8b `888' `888b.     `8'      .888.      `888' d8P'    `Y8  d8P'  `Y8b  `888b.     `8'
888          888      888  888b     d'888   888     888  888   8 `88b.    8      .8"888.      888  Y88bo.      888      888  8 `88b.    8
888          888      888  8 Y88. .P  888   888oooo888'  888   8   `88b.  8     .8' `888.     888   `"Y8888o.  888      888  8   `88b.  8
888          888      888  8  `888'   888   888    `88b  888   8     `88b.8    .88ooo8888.    888       `"Y88b 888      888  8     `88b.8
`88b    ooo  `88b    d88'  8    Y     888   888    .88P  888   8       `888   .8'     `888.   888  oo     .d8P `88b    d88'  8       `888
 `Y8bood8P'   `Y8bood8P'  o8o        o888o o888bood8P'  o888o o8o        `8  o88o     o8888o o888o 8""88888P'   `Y8bood8P'  o8o        `8


history = {_("afficher l'historique des commandes")}
&& : {_("Permet d'exécuter plusieurs commandes dans une seule ligne, en enchaînant leur exécution. ( La commande suivante ne s'exécute que si la précédente réussit. )")}



                                                           {GRIS}        ##.               
                                                           {GRIS}         ###              
                                                           {GRIS}       -#####*            
                                                {BLANC}*****      {GRIS}      #########           
                                               {BLANC}*******     {GRIS}    *############         
                                               {BLANC}*********   {GRIS}   ###############        
                                                {BLANC}:********  {GRIS} ############+            
                                                  {BLANC}*********{GRIS}############              
                                                 {BLANC}************{GRIS}########                
      {ROUGE[0]}                                         =*****{BLANC}*********{GRIS}######                 
      {ROUGE[0]}                                        *********{BLANC}*********{GRIS}##                   
      {ROUGE[0]}                                      *************{BLANC}********{GRIS}#                   
      {ROUGE[0]}                                     ******   ******{BLANC}*********                  
      {ROUGE[0]}                                   ******      ******{BLANC}*********                 
      {ROUGE[0]}                                  ******         ******{BLANC}*********               
      {ROUGE[0]}                                ********          *******{BLANC}********              
      {ROUGE[0]}                              -***********          *******{BLANC}*******             
      {ROUGE[0]}                             ******  ******-       +*****   {BLANC}*****              
      {ROUGE[0]}                           ******      ******     ******                       
      {ROUGE[0]}                          ******        -****** ******                         
      {ROUGE[0]}                        ********          ***********                          
      {ROUGE[0]}                       ***********          *******                            
      {ROUGE[0]}                     ******  :*****         *****:                             
      {ROUGE[0]}                   -*****      ******     ******                               
      {ROUGE[0]}                  ******         *****  +*****                                 
      {ROUGE[0]}                ********          ***********                                  
      {ROUGE[0]}               ***********          *******                                    
      {ROUGE[0]}             ******  ******         ******                                     
      {ROUGE[0]}            *****-     ******     ******                                       
      {ROUGE[0]}          ++++**        ******=  *****:                                        
      {ROUGE[0]}        -+++++            ***********                                          
      {ROUGE[0]}       ++++++              -*******                                            
      {ROUGE[0]}      +++++                 ******                                             
      {ROUGE[0]}     +++++                ******                                               
      {ROUGE[0]}    +++++                *****+                                                
      {ROUGE[0]}    ++++               ******                                                  
      {ROUGE[0]}    ++++              ++***.                                                   
      {ROUGE[0]}    +++++           +++++*                                                     
      {ROUGE[0]}     ++++=        ++++++                                                       
      {ROUGE[0]}     =++++++    +++++++                                                        
      {ROUGE[0]}      +++++++++++++++                                                          
      {ROUGE[0]}    +++  ++++++++++                                                            
      {ROUGE[0]}   ++                                                                          
      {ROUGE[0]} ++:                                                                           
     {ROUGE[0]}=++                                                                             
     {ROUGE[0]}+{VERT}

injection / inject = {_("Permet d'injecter du code python directement dans le programme.")}
                    {_("Utile pour créer des mods et ajouter des code personalisser. 'from mode import *' ajoute le contenue de mode.py au Terminal.")}


""" + RESET
  return data