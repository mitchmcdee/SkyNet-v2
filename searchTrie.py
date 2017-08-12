import pickle
import sys
import os
from trie import Trie, TrieNode

state = ['m', 'e', 'a', 't']
words = [1]

if os.path.exists('words.pickle'):
    print('Must first generate a trie (words.pickle) to search')
    sys.exit(0)

with open('words.pickle', 'rb', errors='ignore') as f:
    print(f)