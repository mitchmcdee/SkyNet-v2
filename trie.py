class Trie():
    def __init__(self):
        self.root = TrieNode('_', 0)

    def addToTrie(self, string):
        head = self.root
        for char in string:
            if char not in head.children:
                head.addChild(TrieNode(char, head.depth + 1))
            head = head.children[char]

    def getMaxDepth(self, head):
        maxDepth = head.depth
        for child in head.children.values():
            maxDepth = max(maxDepth, self.getMaxDepth(child))

        return maxDepth

class TrieNode():
    def __init__(self, value, depth):
        self.value = value
        self.depth = depth
        self.children = {}
        
    def addChild(self, node):
        self.children[node.value] = node