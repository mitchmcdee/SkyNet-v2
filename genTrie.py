import pickle
import sys
import os
from Trie import Trie, TrieNode

# Generates a trie when given a file and optionally the maximum amount of words to add
def genTrie(fileName, maxWords):
    trie = Trie()

    numWords = 0
    with open(fileName, "r") as f:

        # Loop over words an add them to the Trie
        for i, word in enumerate(f):
            numWords += trie.addWord(word.strip('\n'))
            if numWords >= maxWords:
                break

    print("Trie generated! Added " + str(numWords) + " words.")
    print("Dumping to .pickle file")
    # Save to .pickle file
    with open(fileName.split('.')[0] + '.pickle', 'wb') as f:
        pickle.dump(trie, f, pickle.HIGHEST_PROTOCOL)
        print("Dump complete (lol)")

# Check file
if len(sys.argv) == 1 or not os.path.exists(sys.argv[1]):
    print('Must provide a valid word list file')
    sys.exit(0)

# Check word limit
if len(sys.argv) > 2 and not sys.argv[2].isdigit():
    print('Must provide a valid word limit')
    sys.exit(0)

fileName = sys.argv[1]
maxWords = int(sys.argv[2]) if len(sys.argv) == 3 else sys.maxsize

# Generate Trie
genTrie(fileName, maxWords)