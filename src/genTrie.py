#!/usr/bin/env python3
import pickle
import sys
import os
from Trie import Trie, TrieNode

# Check word limit
if len(sys.argv) > 1 and not sys.argv[1].isdigit():
    print('Must provide a valid word limit')
    sys.exit(0)

maxWords = int(sys.argv[1]) if len(sys.argv) == 2 else sys.maxsize
trie = Trie()

# Generate Trie
numWords = 0
with open('../resources/words.txt', "r") as f:
    # Loop over words an add them to the Trie
    for i, word in enumerate(f):
        numWords += trie.addWord(word.strip('\n'))
        if numWords >= maxWords:
            break

print("Trie generated! Added " + str(numWords) + " words.")
print("Dumping to words.pickle file")
# Save to .pickle file
with open('../resources/words.pickle', 'wb') as f:
    pickle.dump(trie, f, pickle.HIGHEST_PROTOCOL)
    print("Dump complete (lol)")