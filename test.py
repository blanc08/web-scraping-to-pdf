import os

dictionary = {
    "name": None,
    "class": None,
    "age": None,
}

items = [dictionary, dictionary, dictionary, dictionary]

max_header = {
    "index": 0,
    "length": 0,
}

for index, value in enumerate(items):
    length = len(value.keys())
    if length > max_header["length"]:
        max_header["length"] = length
        max_header["index"] = index

print(max_header)
