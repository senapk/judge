class Cat:
    def __init__(self, name, label, description):
        self.name = name
        self.label = label
        self.description = description

    def __str__(self):
        return self.name + ":" + self.label + ":" + self.description

cdict = {}
cdict["sel"] = Cat("sel", "sel")
ref = cdict["sel"]
cdict["sel"].desc = "selecao"
print(ref.desc)