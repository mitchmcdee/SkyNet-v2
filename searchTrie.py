#!/usr/bin/python3

import pickle
import sys
import os
from trie import Trie, TrieNode
from state import State

state = State(['a', 'b', 'l', 'e'])
words = [1]

if os.path.exists('words.pickle') is not True:
    print('Must first generate a trie (words.pickle) to search')
    sys.exit(0)

with open('words.pickle', 'rb') as f:
    t = pickle.load(f)

if t is None:
    print('There was a problem loading in the pickle file')
    sys.exit(0)

print(state.getChildrenFromPoint(0, 0))