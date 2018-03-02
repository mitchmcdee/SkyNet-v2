# Trie Tree that holds a dictionary of words
class Trie():
    def __init__(self):
        self.root = TrieNode('_')
        self.words = set()

    # Add a word to the Trie
    def addWord(self, word):
        if word in self.words:
            return

        head = self.root
        for char in word:
            if char not in head.children:
                head.addChild(TrieNode(char))
            head = head.children[char]

        self.words.add(word)
        # Symbolise end of a word
        head.children['*'] = None

    # Check whether given word is in the Trie
    def isWord(self, word):
        return word in self.words

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