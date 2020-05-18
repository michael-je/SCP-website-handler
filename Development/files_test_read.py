import pickle
# from files_test_write import TestClass


filename = 'test_file'
with open(filename, 'rb') as file:
    ls = pickle.load(file)

print(ls)
for i in ls:
    print(i.value)
