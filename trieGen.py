#!/usr/bin/python3

import pickle
import sys
from trie import Trie, TrieNode

def genTrie(maxWords):
    t = Trie()

    longestWord = 0
    with open("words.txt", "r") as f:
        for i,word in enumerate(f):
            if i > maxWords:
                break

            longestWord = max(longestWord, len(word.strip('\n')))
            t.addToTrie(word.strip('\n'))

    print("Longest word length was: " + str(longestWord))

    with open('words.pickle', 'wb') as f:
        pickle.dump(t, f, pickle.HIGHEST_PROTOCOL)

    print("Trie generated")


def validateTrie():
    with open('words.pickle', 'rb') as f:
        t = pickle.load(f)
        if isinstance(t, Trie):
            print("Trie is VALID")
            return t
        else:
            print("Trie is INVALID")


if len(sys.argv) >= 2 and sys.argv[1] == 'gen':
    numWords = sys.maxsize
    if len(sys.argv) == 3:
        numWords = int(sys.argv[2])

    genTrie(numWords)

elif len(sys.argv) == 2 and sys.argv[1] == 'read':
    t = validateTrie()
    if t is not None:
        print("Longest word length in trie is: " + str(t.getMaxDepth(t.root)))

else:
    print("Must be 'gen' or 'read'")