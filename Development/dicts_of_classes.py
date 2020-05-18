class NewClass:
    def __init__(self, value):
        self.value = value


dict_of_classes = {}

for i in range(10):
    dict_of_classes[i] = NewClass(i+10)

for i in range(10):
    print(dict_of_classes[i].value)

for i in range(10):
    dict_of_classes[i].value = i + 20

for i in range(10):
    print(dict_of_classes[i].value)