class Object:
    def __init__(self, name):
        self.name = name


o1 = Object('a')
o2 = o1
o3 = o2

print(o1 is o2)
print(o2 is o3)
print(o1 is o3)