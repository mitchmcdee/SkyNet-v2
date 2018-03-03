# Trie Tree that holds a dictionary of words
class Trie():

    # Trie Node that represents a character value and its children in the Trie
    class TrieNode():
        def __init__(self, value):
            self.value = value
            self.children = {}

        # Add a child node
        def add_child(self, node):
            self.children[node.value] = node

        # Checks whether the given character is a child of the node
        def is_child(self, char):
            return char in self.children

        # Returns the child node of the given char
        def child(self, char):
            return self.children.get(char, None)


    def __init__(self):
        self.root = self.TrieNode('_')
        self.words = set()

    # Add a word to the Trie
    def add_word(self, word):
        if word in self.words:
            return
        head = self.root
        for char in word:
            if not head.is_child(char):
                head.add_child(self.TrieNode(char))
            head = head.child(char)
        self.words.add(word)

    # Check whether given word is in the Trie
    def is_word(self, word):
        return word in self.words

    # Check whether given path is in the Trie
    def is_path(self, path):
        head = self.root
        for char in path:
            if char not in head.children:
                return False
            head = head.children[char]
        return True
