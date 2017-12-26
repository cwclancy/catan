###############################################################################
# checks if the player is making leagal catan moves
###############################################################################
from boardLogic import *



# at beggining each person can place 2 houses and 2 roads
# anywhere, then roads can only be placed if they're touching other
# roads, and houses can only be placed if they are touching a road
# and eat least two sides away from all other houses

def getNode(x, y):
    for vertex in GameBoard.boardVerticies:
        if x == vertex[1][0] and y == vertex[1][1]:
            return vertex[2]


def legalRoad(s, c):
    touchingHouse = False
    touchingRoad = False
    empty = GameBoard.boardSides[s][2] == 0


    # check if it is touching a house
    houseCheck1 = (GameBoard.boardSides[s][1][0], \
        GameBoard.boardSides[s][1][1])
    houseCheck2 = (GameBoard.boardSides[s][1][2], \
        GameBoard.boardSides[s][1][3])
    myColor = c

    for i in range(len(GameBoard.boardVerticies)):
        house = GameBoard.boardVerticies[i][1]
        color = GameBoard.boardVerticies[i][0]
        if (houseCheck1 == house or houseCheck2 == house) \
        and myColor == color:
            touchingHouse = True

    # check if touching road
    for i in range(len(GameBoard.boardSides)):
        sideCoors = GameBoard.boardSides[i]
        side1 = (sideCoors[1][0], sideCoors[1][1])
        side2 = (sideCoors[1][2], sideCoors[1][3])
        color = GameBoard.boardSides[i][2]
        if (((houseCheck1 == side1 or houseCheck1 == side2) or\
            (houseCheck2 == side1 or houseCheck2 == side2)) and \
        color == myColor):
            touchingRoad = True

    antiHouseCheck1 = getNode(GameBoard.boardSides[s][1][0],\
        GameBoard.boardSides[s][1][1])
    antiHouseCheck2 = getNode(GameBoard.boardSides[s][1][2],\
        GameBoard.boardSides[s][1][3])

    vertex = GameBoard.boardVerticies

    return (touchingHouse or touchingRoad) and empty



def startLegalHouse(v, c):
    twoAway = True
    empty = GameBoard.boardVerticies[v][0] == 0

    myPos = GameBoard.boardVerticies[v][1]
    # check directly surrounding
    # find roads
    firstHop = []
    for i in range(len(GameBoard.boardSides)):
        side = GameBoard.boardSides[i][1]
        side1 = (side[0],side[1])
        side2 = (side[2],side[3])
        if side1 == myPos:
            firstHop.append(side2)
        if side2 == myPos:
            firstHop.append(side1)

    checkAll = firstHop

    # make sure that there is at least a road between
    for pos in checkAll:
        for i in range(len(GameBoard.boardVerticies)):
            verticie = GameBoard.boardVerticies[i][1]
            color = GameBoard.boardVerticies[i][0]
            if pos == verticie:
                if color != 0:
                    twoAway = False

    return twoAway and empty

def gameLegalHouse(v, c):
    twoHop = startLegalHouse(v, c)
    touchingRoad = False

    myPos = GameBoard.boardVerticies[v][1]
    myColor = c
    # check for my roads touching
    for i in range(len(GameBoard.boardSides)):
        side = GameBoard.boardSides[i]
        color = side[2]
        side1 = (side[1][0],side[1][1])
        side2 = (side[1][2],side[1][3])
        if (myPos == side1 or myPos == side2) and color == myColor:
            touchingRoad = True

    return twoHop and touchingRoad

