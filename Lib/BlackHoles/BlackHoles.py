class BlackHoles:
    """
    ---- 🇫🇷 Français ----

    - Objectif
    - Ce mécanisme permet de simplifier la gestion des arguments optionnels (fonctions, classes, objets…). Il évite les tests conditionnels du type if key is not None, tout en assurant un comportement par défaut sûr, silencieux et cohérent.
    
    - Principe
    - On utilise une instance spéciale comme BlackHoles() en paramètre par défaut. Cet objet :
    
        - Accepte dynamiquement toutes les méthodes et attributs (.add(), .log(), .anything()…),
    
        - Renvoie toujours un objet non vide (ex. un str) ⇒ évalué comme True,
    
        - Ignore tout sans effet de bord, sans jamais lever d'erreur,
    
        - Sert de trou noir logique : il absorbe silencieusement tout ce qu’on lui envoie.
    
    - Exemple à remplacer (avec condition):❌

    def fonction(key=None):
        if key:
            key.add("data")
    
            
    - Version propre avec BlackHoles: ✅

    def fonction(key=BlackHoles()):
        key.add("data")

        
    ✅ Aucun if, aucune erreur, même si aucun objet réel n’est fourni.

    ✅ key peut être un vrai objet ou un BlackHoles — le code fonctionne toujours.

    
    ---- 🇺🇸 English ----

    
    - Objective
    - This mechanism simplifies the handling of optional arguments (functions, classes, objects, etc.). It avoids conditional checks like if key is not None, while ensuring a default behavior that is safe, silent, and consistent.
    
    - Principle
    - A special instance like BlackHoles() is used as a default parameter. This object:
    
        - Dynamically accepts all methods and attributes (.add(), .log(), .anything(), etc.),
    
        - Always returns a non-empty object (e.g., a str) ⇒ evaluated as True,
    
        - Ignores everything without side effects, never raising an error,
    
        - Acts as a logical black hole: it silently absorbs everything sent to it.
    
    - Example to replace (with condition): ❌
    
    def fonction(key=None):
        if key:
            key.add("data")


    - Clean version with BlackHoles: ✅
    
    def fonction(key=BlackHoles()):
        key.add("data")
    
    ✅ No if, no errors, even if no actual object is provided.
    
    ✅ key can be a real object or BlackHoles — the code always works.

    """
    def __init__(self):
        pass

    def __getattr__(self, name):
        return BlackHoles()

    def __call__(self, *args, **kwargs):
        return self

    def __repr__(self):
        return "<>"