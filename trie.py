class Trie():
    def __init__(self):
        self.root = TrieNode('_', 0)

    def addToTrie(self, string):
        head = self.root
        for char in string:
            if char not in head.children:
                head.addChild(TrieNode(char, head.depth + 1))
            head = head.children[char]

        # Symbolise end of a word
        head.children['*'] = None

    def getMaxDepth(self, head):
        maxDepth = head.depth
        for child in head.children.values():
            maxDepth = max(maxDepth, self.getMaxDepth(child))

        return maxDepth

    def isWord(self, word):
        head = self.root
        for char in word:
            if char not in head.children:
                return False
            head = head.children[char]

        return True if '*' in head.children else False

class TrieNode():
    def __init__(self, value, depth):
        self.value = value
        self.depth = depth
        self.children = {}
        
    def addChild(self, node):
        self.children[node.value] = node