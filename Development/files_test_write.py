# https://stackoverflow.com/questions/4529815/saving-an-object-data-persistence
# https://stackoverflow.com/questions/17076873/python-how-to-save-a-list-with-objects-in-a-file

import pickle

class TestClass:
    def __init__(self, value):
        self.value = value


instances = []

for i in range(10):
    instances.append(TestClass(i))

data = instances
filename = 'test_file'
with open(filename, 'wb') as output:
    pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)
