import sys
from math import sqrt
from copy import deepcopy

directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

class State():
    def __init__(self, state):
        sideLength = sqrt(len(state))

        # Check input state is a perfect square
        if (sideLength != int(sideLength)):
            print("Input state is not a perfect square")
            sys.exit(0)

        # Check all chars are valid
        if not all([str(c).isalpha() or c == '_' for c in state]):
            print("Input contains illegal chars")
            sys.exit(0)

        self.state = state
        self.sideLength = int(sideLength)


    def getChildrenFromPoint(self, pointIndex):
        children = []
        for child in directions:
            childX = pointIndex % self.sideLength + child[0]
            childY = pointIndex // self.sideLength + child[1]

            if childX < 0 or childY < 0 or childX >= self.sideLength or childY >= self.sideLength:
                continue

            childIndex = childX + childY * self.sideLength

            # Skip over children which are underscores (i.e. empty space)
            if self.state[childIndex] == '_':
                continue

            children.append(childIndex)

        return children


    def getWords(self):
        words = []

        for i,_ in enumerate(self.state):
            if v == '_':
                continue

            root = StateNode(i, self.state[i], None)
            stack = [root]
            visited = set()

            while len(stack) != 0:
                current = stack.pop()

                for c in self.getChildrenFromPoint(current.index):
                    if current.hasParent(c):
                        continue

                    child = StateNode(c, self.state[c], current)
                    current.addChild(child)
                    stack.append(child)

            words.extend(root.getWords())

        return words


    def getRoots(self):
        roots = []

        for i,v in enumerate(self.state):
            if v == '_':
                continue

            root = StateNode(i, self.state[i], None)
            stack = [root]
            visited = set()

            while len(stack) != 0:
                current = stack.pop()

                for c in self.getChildrenFromPoint(current.index):
                    if current.hasParent(c):
                        continue

                    child = StateNode(c, self.state[c], current)
                    current.addChild(child)
                    stack.append(child)

            roots.append(root)

        return roots


    def getWordFromPath(self, path):
        return ('').join([self.state[i] for i in path])


    def getRemovedWordState(self, path):
        newState = deepcopy(self.state)

        # Replace path with underscores (i.e. empty space)
        for i in path:
            newState[i] = '_'

        return newState


class StateNode():
    def __init__(self, index, value, parent):
        self.index = index
        self.value = value
        self.parent = parent
        self.children = {}


    def addChild(self, child):
        self.children[child.index] = child


    def hasParent(self, parentIndex):
        head = self
        while head is not None:
            if head.index == parentIndex:
                return True

            head = head.parent

        return False


    def printChildren(self):
        print(self.value, self.children)
        for child in self.children.values():
            printChildren(child)


    def getWords(self):
        words = [[self.value]]
        for child in self.children.values():
            words.extend([[self.value] + child for child in child.getWords()])
    
        return words


    def getPaths(self):
        paths = [[self.index]]
        for child in self.children.values():
            paths.extend([[self.index] + child for child in child.getPaths()])
    
        return paths


    def getLongestWord(self):
        return max(self.getWords(), key=len)


    def getLongestPath(self):
        return max(self.getPaths(), key=len)