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

    def getChildrenFromPoint(self, i, j):
        pointIndex = i + self.sideLength * j

        children = []
        for child in directions:
            childX = pointIndex % self.sideLength + child[0]
            childY = pointIndex // self.sideLength + child[1]

            if childX < 0 or childY < 0 or childX >= self.sideLength or childY >= self.sideLength:
                continue

            childIndex = childX + childY * self.sideLength
            children.append(self.state[childIndex])

        return children