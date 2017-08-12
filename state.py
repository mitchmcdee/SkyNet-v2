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


    def getValidPathRoots(self, trie):
        roots = []

        for i,v in enumerate(self.state):
            if v == '_':
                continue

            root = StateNode(i, self.state[i], {}, [self.state[i]])
            stack = [root]

            while len(stack) != 0:
                current = stack.pop()

                for c in self.getChildrenFromPoint(current.index):
                    if c in current.parents:
                        continue

                    childPath = deepcopy(current.path) + [self.state[c]]

                    if trie.isPath(childPath) is not True:
                        continue

                    child = StateNode(c, self.state[c], deepcopy(current.parents), childPath)
                    child.addParent(current)
                    current.addChild(child)
                    stack.append(child)

            roots.append(root)

        return roots


    def getWordFromPath(self, path):
        return ('').join([self.state[i] for i in path])


    def getRemovedWordState(self, path):
        newState = deepcopy(self)

        # Replace path with underscores (i.e. empty space)
        for i in path:
            newState.state[i] = '_'

        # If tiles need to be dropped down, do so
        for i,v in enumerate(newState.state):
            if v != '_':
                continue

            # Check above cell is valid and not an underscore
            aboveCellIndex = i - self.sideLength
            if aboveCellIndex < 0 or newState.state[aboveCellIndex] == '_':
                continue

            # Swap tiles
            temp = v
            newState.state[i] = newState.state[aboveCellIndex]
            newState.state[aboveCellIndex] = temp

        return newState


    def printState(self):
        for i in range(self.sideLength):
            multiplier = i * self.sideLength
            print(self.state[multiplier : self.sideLength + multiplier])


class StateNode():
    def __init__(self, index, value, parents, path):
        self.index = index
        self.value = value
        self.parents = parents
        self.children = {}
        self.path = path


    def addChild(self, child):
        self.children[child.index] = child


    def addParent(self, parent):
        self.parents[parent.index] = None


    def printChildren(self):
        print(self.value, self.children)
        for child in self.children.values():
            printChildren(child)


    # optimise this?
    def getPaths(self):
        paths = [[self.index]]
        for child in self.children.values():
            paths.extend([[self.index] + child for child in child.getPaths()])
    
        return paths


    def getValidPaths(self, trie, state, wordLength):
        validLengths = list(filter(lambda x: len(x) == wordLength, self.getPaths()))
        if len(validLengths) == 0:
            return None

        validPaths = list(filter(lambda x: trie.isWord(state.getWordFromPath(x)), validLengths))
        if len(validPaths) == 0:
            return None

        return validPaths

