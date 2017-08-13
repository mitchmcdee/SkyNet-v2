# Trie Tree that holds a dictionary of words
class Trie():
    def __init__(self):
        self.root = TrieNode('_')

    # Add a word to the Trie
    def addWord(self, word):
        head = self.root
        for char in word:
            if char not in head.children:
                head.addChild(TrieNode(char))
            head = head.children[char]

        # Return 0 if word already exists, else 1
        if '*' in head.children:
            return 0

        # Symbolise end of a word
        head.children['*'] = None
        return 1

    # Check whether given word is in the Trie
    def isWord(self, word):
        head = self.root
        for char in word:
            if char not in head.children:
                return False
            head = head.children[char]

        return True if '*' in head.children else False

    # Check whether given path is in the Trie
    def isPath(self, path):
        head = self.root
        for char in path:
            if char not in head.children:
                return False
            head = head.children[char]

        return True


# Trie Node that represents a character value and its children in the Trie
class TrieNode():
    def __init__(self, value):
        self.value = value
        self.children = {}

    # Add a child node
    def addChild(self, node):
        self.children[node.value] = node