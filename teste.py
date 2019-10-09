class Cat:
    def __init__(self):
        self.name = "name"
        self.pulgas = []

cat = Cat()

print(type(getattr(cat, "name")) is list)
print(type(getattr(cat, "pulgas")) is list)