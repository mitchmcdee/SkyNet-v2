import pickle
import sys

class Trie():
    def __init__(self):
        self.root = Node('_', 0)

    def addToTrie(self, string):
        head = self.root
        for char in string:
            if char not in head.children:
                head.addChild(Node(char, head.depth + 1))
            head = head.children[char]

    def getMaxDepth(self, head):
        maxDepth = head.depth
        for child in head.children.values():
            maxDepth = max(maxDepth, self.getMaxDepth(child))

        return maxDepth


class Node():
    def __init__(self, value, depth):
        self.value = value
        self.depth = depth
        self.children = {}
        
    def addChild(self, node):
        self.children[node.value] = node


def genTrie():
    t = Trie()

    longestWord = 0
    with open("words.txt", "r") as f:
        for i,word in enumerate(f):
            # if i > 1000:
            #     break

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


if (len(sys.argv) == 2):
    if sys.argv[1] == 'gen':
        genTrie()
    elif sys.argv[1] == 'read':
        t = validateTrie()
        if t is not None:
            print("Longest word in trie is: " + str(t.getMaxDepth(t.root)))
else:
    print("Must be 'gen' or 'read'")