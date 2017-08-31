#!/usr/bin/env python3
import os

BASE = '../resources/'

# Dictionary holding word lists
words = {}

# Root file containing words of various lengths
with open(BASE + 'bigWords.txt', 'r') as f:
    for line in f:
        word = line.strip('\n')
        length = str(len(word))

        # add word to existing list or make a new list
        if length in words:
            words[length].append(word)
        else:
            words[length] = [word]

# Remove old word files
for i in range(20):
    path = BASE + str(i) + '.txt'
    if os.path.exists(path):
        os.remove(path)

# Add new word files
for i,length in words.items():
    with open(BASE + i + '.txt', 'w') as f:
        for word in sorted(length):
            f.write(word + '\n')