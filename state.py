import sys
from math import sqrt

directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

class State():
    def __init__(self, state):
        sideLength = sqrt(len(state))

        # Check input state is a perfect square
        if (sideLength != int(sideLength)):
            print("Input state is not a perfect square")
            sys.exit(0)

        # Check all chars are valid
        if not all([str(c).isalpha() for c in state]):
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
            children.append(childIndex)

        return children

    def getWords(self):
        words = []

        for i,_ in enumerate(self.state):
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
        paths = [[self.value]]
        for child in self.children.values():
            paths.extend([[self.value] + child for child in child.getWords()])
    
        return paths