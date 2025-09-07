# 🧰 Contribution et développement de Winion

Bienvenue dans le projet Winion !

---



# Licence des modules dans `Lib/`

Sauf indication contraire spécifiée explicitement dans un module ou fichier particulier de `Lib/`,  
tous les modules contenus dans ce dossier sont soumis à la même licence que le projet principal.

En d’autres termes, **si aucune licence propre n’est mentionnée dans un module de `Lib/`, alors il hérite automatiquement de la licence générale du projet Winion.**




## Structure du projet

Ce fichier explique rapidement la différence importante entre deux dossiers clés du projet : `Lib` et `src`.

### `src/`

- Contient **le code source principal** du projet Winion.
- Ce sont les fichiers et modules développés **spécifiquement pour Winion**.
- Toute nouvelle fonctionnalité, correction, ou amélioration du projet se fait ici.

### `Lib/`

- Contient des **bibliothèques et modules Python développés séparément**.
- Ce sont des projets à part entière que j'ai créés indépendamment, puis **réutilisés ici**.
- Ces modules sont généralement plus génériques et peuvent être utilisés dans d'autres projets aussi.

---

# Catégories de paquets – Types d’installation dans Winion
# Chaque module Winion est classé par type, selon sa méthode d’installation et son niveau d’intégration dans le gestionnaire de paquets.

<details>
    <summary><strong>Type 0 (Integrated Package)</strong></summary>
        Ce type de module est entièrement géré par Winion.
        Il s’agit généralement d’une archive contenant les fichiers du module à extraire automatiquement dans un dossier standard (ex. /module/<nom>).
        Aucun script externe, installeur ou étape manuelle n’est requis.
        Winion contrôle entièrement le processus : extraction, intégration, mise à jour, suppression, et versioning.
        Ce type offre la meilleure compatibilité avec le système de paquets Winio
</details>

<details>
    <summary><strong>Type 1</strong></summary>
        Ce type est réservé pour de futurs formats personnalisés (non définis actuellement).
</details>

<details>
    <summary><strong>Type 2</strong></summary>
        Ce type est réservé pour de futurs formats personnalisés (non définis actuellement).
</details>

<details>
    <summary><strong>Type 3 (Standalone Installer)</strong></summary>
        Ce type de module est un installeur autonome (par exemple .exe, .msi) fourni directement par l'éditeur du logiciel.
        Il est non géré par Winion : aucune extraction, vérification, versioning ou intégration ne sont effectués.
        Winion se contente de fournir le fichier et de l'exécuter une seule fois lors de l'installation.
        Une fois l’installation terminée, Winion ne suit pas l’état du programme installé.
</details>


## Bonnes pratiques

- Pour ajouter une nouvelle fonctionnalité propre au projet Winion, modifie ou ajoute dans `src/`.
- Si tu souhaites améliorer ou corriger une bibliothèque tierce dans `Lib/`, fais-le en gardant en tête que ce code est partagé.
- Respecte la structure existante pour faciliter la maintenance et la compréhension.

---

Merci de contribuer au projet !
