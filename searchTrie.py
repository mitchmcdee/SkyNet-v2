#!/usr/bin/python3

import pickle
import sys
import os
from trie import Trie, TrieNode
from state import State, StateNode
from queue import Queue

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

words = []
for i,_ in enumerate(state.state):

    root = StateNode(i, state.state[i], None)
    queue = Queue()
    visited = set()
    queue.put(root)

    print("Searching down " + root.value)

    while not queue.empty():
        current = queue.get()

        for c in state.getChildrenFromPoint(current.index):
            if current.hasParent(c):
                continue

            child = StateNode(c, state.state[c], current)
            current.addChild(child)
            queue.put(child)

    words.extend(root.getWords())

print(words)



