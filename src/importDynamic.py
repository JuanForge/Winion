Prototype = True


import importlib.util
class importDynamic:
    def Script(fichier=''):
        spec = importlib.util.spec_from_file_location("temp", fichier)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        temp = False
        
        Fonction = module # module.Start.Start
        return Fonction 
