import pickle
import sys

class Trie():
    def __init__(self):
        self.root = Node('_')

    def addToTrie(self, string):
        head = self.root
        for char in string:
            if char not in head.children:
                head.addChild(Node(char))
            head = head.children[char]


class Node():
    def __init__(self, value):
        self.value = value
        self.children = {}
        
    def addChild(self, node):
        self.children[node.value] = node

    def __str__(self):
        return str(self.value)


def genTrie():
    t = Trie()

    with open("words.txt", "r") as f:
        for word in f:
            t.addToTrie(word.strip('\n'))

    with open('words.pickle', 'wb') as f:
        pickle.dump(t, f, pickle.HIGHEST_PROTOCOL)

    print("Trie generated")


def validateTrie():
    with open('words.pickle', 'rb') as f:
        if isinstance(pickle.load(f), Trie):
            print("Trie is VALID")
        else:
            print("Trie is INVALID")


if (len(sys.argv) == 2):
    if sys.argv[1] == 'gen':
        genTrie()
    elif sys.argv[1] == 'read':
        validateTrie()
else:
    print("Must be 'gen' or 'read'")