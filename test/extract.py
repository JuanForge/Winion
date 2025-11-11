import ast
import os
import polib

class Extractor(ast.NodeVisitor):
    def __init__(self, filename=None):
        self.filename = filename
        self.messages = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "_":
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    self.messages.append((arg.value, node.lineno))
        self.generic_visit(node)

    def extract_messages_from_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
        self.messages = []
        self.filename = filepath
        self.visit(tree)
        return self.messages

    def generate_pot_from_files(self, paths, output_pot):
        all_files = []
        for path in paths:
            if os.path.isfile(path) and path.endswith(".py"):
                all_files.append(path)
            elif os.path.isdir(path):
                for dirpath, _, filenames in os.walk(path):
                    for fname in filenames:
                        if fname.endswith(".py"):
                            all_files.append(os.path.join(dirpath, fname))

        po = polib.POFile()
        po.metadata = {
            "Project-Id-Version": "Winion 1.0",
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=utf-8",
        }

        seen = {} 

        for f in all_files:
            for msg, lineno in self.extract_messages_from_file(f):
                if msg in seen:
                    seen[msg].occurrences.append((f, lineno))
                else:
                    entry = polib.POEntry(msgid=msg, msgstr="", occurrences=[(f, lineno)])
                    po.append(entry)
                    seen[msg] = entry

        os.makedirs(os.path.dirname(output_pot) or ".", exist_ok=True)
        po.save(output_pot)

if __name__ == "__main__":
    paths = ["code.py", "Winion"]
    extractor = Extractor()
    extractor.generate_pot_from_files(paths, "Winion.pot")
    print(f"PO généré pour {len(paths)} chemins (fichiers/dossiers).")
    