###############################################################################
# Connor Clancy
# client file
# handles the client and server messages and draws the game
# creates the user experience
# drawn in tkinter with the assistance of the 112 run function
# sockets implementaion is based on the framework provided by
# Rohan Varma and Kyle Chin
###############################################################################

import socket
import threading
import deck
import itertools
import sys
import pickle
from queue import Queue
from tkinter import *
from boardLogic import *
from easyGameInit import *
from chance import *
from legalMove import *
from login import *

# sockets client famework based on framework from Rohan Varma and Kyle Chin
# run function from 112 website
# images cite in images folder


# set up host and port for users
# change host to your ip in here, the server, and ai, to
# play on multiple computers
HOST = ""
PORT = 50003

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((HOST, PORT))
print("Connected to server")

def handleServerMsg(server, serverMsg):
  server.setblocking(1)
  msg = ""
  command = ""
  while True:
    msg += server.recv(10).decode("UTF-8")
    command = msg.split("\n")
    while (len(command) > 1):
      readyMsg = command[0]
      msg = "\n".join(command[1:])
      serverMsg.put(readyMsg)
      command = msg.split("\n")


#############################################################################
# score related
#############################################################################


def checkGameOver(data):
    for key in state.scores:
        if state.scores[key] >= state.winCondtion:
            state.gameOver = True
            message = "gameOver " + str(state.scores[state.myID]) + "\n"
            data.server.send(message.encode())
            if state.scores[state.myID] >= state.winCondtion:
                state.winner = state.myID


#
def playerLongestRoad():
    lRoad = 0
    lPlayer = ""
    roadScores = {}
    listRoadScores = []
    currentLongestRoad = state.currentLongestRoad
    currentLongestRoadLength = state.currentLongestRoadLength
    roadScores["Player1"] = longestRoad(1)
    roadScores["Player2"] = longestRoad(2)
    roadScores["Player3"] = longestRoad(3)
    roadScores["Player4"] = longestRoad(4)

    for key in roadScores:
        listRoadScores.append(roadScores[key])
        if roadScores[key] > lRoad:
            lRoad = roadScores[key]
            lPlayer = key
    if lRoad >= 5 and lRoad >= currentLongestRoadLength \
        and listRoadScores.count(max(listRoadScores)) == 1:
        if currentLongestRoad == lPlayer or currentLongestRoad == "":
            state.scores[lPlayer] += 2
        else:
            # remove old longest roads points
            state.scores[currentLongestRoad] -= 2
            # give new longest road points
            state.scores[lPlayer] += 2

        state.currentLongestRoad = lPlayer
        state.currentLongestRoadLength = lRoad

def updateScore(data):
    p1Score = 0
    p2Score = 0
    p3Score = 0
    p4Score = 0
    houseCheck = set(state.buildHouses)
    for house in houseCheck:
        if house[1] == 1:
            p1Score += 1
        if house[1] == 2:
            p2Score += 1
        if house[1] == 3:
            p3Score += 1
        if house[1] == 4:
            p4Score += 1
    cityCheck = set(state.buildCities)
    for city in cityCheck:
        if city[1] == 1:
            p1Score += 1
        if city[1] == 2:
            p2Score += 1
        if city[1] == 3:
            p3Score += 1
        if city[1] == 4:
            p4Score += 1

    for key in state.scores:
        if key == "Player1":
            state.scores[key] = p1Score
        if key == "Player2":
            state.scores[key] = p2Score
        if key == "Player3":
            state.scores[key] = p3Score
        if key == "Player4":
            state.scores[key] = p4Score

    state.scores[state.myID] += state.myHand["Vp"]
    playerLongestRoad()



boardGraph = {
    1 : [4,5],
    2 : [5,6],
    3 : [6,7],
    4 : [1,8],
    5 : [1,2,9],
    6 : [2,3,10],
    7 : [3,11],
    8 : [4,12,13],
    9 : [5,13,14],
    10 : [11,6,15],
    11 : [15,7,16],
    12 : [8,17],
    13 : [8,9,18],
    14 : [9,10,19],
    15 : [10,11,20],
    16 : [11,21],
    17 : [12, 22, 23],
    18 : [23,13,24],
    19 : [24,14,25],
    20 : [25,15,26],
    21 : [26,16,27],
    22 : [17,28],
    23 : [17,29,18],
    24 : [18,19,30],
    25 : [19,20,31],
    26 : [20,21,32],
    27 : [21,33],
    28 : [22,34],
    29 : [34,35,23],
    30 : [35,36,24],
    31 : [36,37,25],
    32 : [37,38,26],
    33 : [38,27],
    34 : [28,29,39],
    35 : [29,30,40],
    36 : [30,31,41],
    37 : [31,32,42],
    38 : [32,33,43],
    39 : [34,44],
    40 : [44,45,35],
    41 : [45,46,36],
    42 : [46,47,37],
    43 : [47,38],
    44 : [39,40,48],
    45 : [40,41,49],
    46 : [41,42,50],
    47 : [42,43,51],
    48 : [44,52],
    49 : [52,53,45],
    50 : [53,54,46],
    51 : [54, 47],
    52 : [48,49],
    53 : [49,50],
    54 : [50,51],
}

def makeAdjacencyList(color):
    adjacencyList = boardGraph.copy()
    verticies = set()
    # find nodes of roads
    for i in range(len(GameBoard.boardSides)):
        if GameBoard.boardSides[i][2] == color:
            check1 = (GameBoard.boardSides[i][1][0],\
                      GameBoard.boardSides[i][1][1])
            check2 = (GameBoard.boardSides[i][1][2],\
                       GameBoard.boardSides[i][1][3])
            for j in range(len(GameBoard.boardVerticies)):
                if check1 in GameBoard.boardVerticies[j][1]:
                    verticies.add(GameBoard.boardVerticies[j][2])
                if check2 in GameBoard.boardVerticies[j][1]:
                    verticies.add(GameBoard.boardVerticies[j][2])

def getNode(x, y):
    for vertex in GameBoard.boardVerticies:
        if x == vertex[1][0] and y == vertex[1][1]:
            return vertex[2]

def longestRoad(color):
    # create the adjancency list
    adjacencyList = {}
    for edge in GameBoard.boardSides:
        if edge[2] == color:
            node1 = getNode(edge[1][0], edge[1][1])
            node2 = getNode(edge[1][2], edge[1][3])
            if node1 in adjacencyList:
                adjacencyList[node1] += [node2]
            else:
                adjacencyList[node1] = [node2]
            if node2 in adjacencyList:
                adjacencyList[node2] += [node1]
            else:
                adjacencyList[node2] = [node1]

    visited = {}
    for key in adjacencyList:
        visited[key] = False

    # returns last visited node if not all visited
    def allVisited(visited = visited):
        for key in visited:
            if visited[key] == False:
                return (False, key)
        return (True, -1)

    edgeCount = 0

    while not allVisited(visited)[0]:
        currCount = 0
        startNode = 0
        nodeStack = [allVisited(visited)[1]]
        while (nodeStack):
            nextNode = nodeStack.pop()
            for i in adjacencyList[nextNode]:
                if not visited[i]:
                    nodeStack.append(i)
                currCount += 1
            visited[nextNode] = True
        edgeCount = max(edgeCount, currCount // 2)

    return edgeCount




#############################################################################
#  7 related
#############################################################################

def rolledSevenSwap():
    global rolledSeven
    rolledSeven = not rolledSeven
    if rolledSeven:
        rolledSevenFunction()

def resetMovingRaider():
    global globalMovingRaiderCheck
    globalMovingRaiderCheck = True



def movingRaiderTrue():
    global movingRaider
    movingRaider = True

def movingRaiderFalse():
    global movingRaider
    movingRaider = False

def moreThanSevenTrue():
    global moreThanSeven
    moreThanSeven = True

def moreThanSevenFalse():
    global moreThanSeven
    moreThanSeven = False


moreThanSeven = False
rolledSeven = False

#widgit related
globalRemoveCards = True
globalMovingRaiderCheck = True

#############################################################################
def removeCardsWidgit(data):
    global globalRemoveCards
    if globalRemoveCards:
        beginLength = len(getListHand(state.myHand))
        globalRemoveCards = False

        cardsToRemove = StringVar()
        removeReq = Entry(data.root, textvariable=cardsToRemove)
        removeReq.pack()
        removeReq.place(x=data.width//2, y=data.height//2, anchor="center")

        def removeCards():
            action = cardsToRemove.get()
            actionList = action.split(" ")
            removeDict = d = dict(itertools.zip_longest\
                (*[iter(actionList)]*2,fillvalue=""))
            for key in removeDict:
                removeDict[key] = int(removeDict[key])
                removeDict[key] *= -1
            updateHand(removeDict)
            state.listHand = getListHand(state.myHand)
            if len(state.listHand) <= beginLength//2:
                moreThanSevenFalse()
                removeReq.destroy()
                submit.destroy()

        submit = Button(data.root, text="Submit", command=removeCards)
        submit.pack()
        submit.place(x=data.width//2, y=data.height//2 + 30,
            anchor="center")


#############################################################################
def movingRaiderWidgit(data):
    global globalMovingRaiderCheck
    if globalMovingRaiderCheck:
        globalMovingRaiderCheck = False

        def finishRaider():
            globalMovingRaiderCheck = True
            resetMovingRaider()
            rolledSevenSwap()
            button.destroy()
            if state.currRaiderPos != state.nextRaiderPos:
                message = "Raider " + str(state.currRaiderPos) + \
                " " + str(state.nextRaiderPos) + "\n"
                data.server.send(message.encode())
            playersToChooseFrom = playersOnHex(data, state.nextRaiderPos)
            movingRaiderFalse()
            while len(playersToChooseFrom) != 0:
                index = random.randint(0,len(playersToChooseFrom)) + 1
                playerToStealFrom = "Player" + str(index)
                if playerToStealFrom == state.myID:
                    continue
                message = "steal " + playerToStealFrom + "\n"
                data.server.send(message.encode())
                break



        button = Button(data.root, text="finished", command=finishRaider)
        button.pack()
        button.place(x=data.width//2, y=19*data.height//20, anchor="center")




#############################################################################
def removeCards(canvas, data, state):
    state.removingCards = True
    canvas.create_rectangle(data.width//5, data.height//5,
                            4*data.width//5, 4*data.height//5,
                            fill="white", width=5)
    canvas.create_text(data.width//2, 3*data.height//6,
            text="Click Until Half", font=("ms Serif", 40))
    state.listHand = getListHand(state.myHand)
    if state.halfFlag:
        state.halfOfSeven = len(state.listHand)//2
        state.halfFlag = False
    canvas.create_text(data.width//2, 2*data.height//3, text="%d" % \
                        (len(state.listHand) - state.halfOfSeven - 1),
                                      font=("ms Serif", 72))
    handCheck = {}
    for key in state.myHand:
        if key != "Knight" and key != "Vp" and key != "RoadBuilding":
            handCheck[key] = state.myHand[key]
    drawHandWithValues(canvas, data, state, 215, 280, 75, 0, handCheck)
    if (len(state.listHand) - state.halfOfSeven - 1) == 0:
        moreThanSevenFalse()
        state.removingCards = False
        state.halfFlag = True
        state.halfOfSeven = 0

def drawMoveRaider(canvas, data, state):
    drawBoard(canvas, data, state)
    canvas.create_text(data.width//2, data.height//7.5, text="Move Raider",
                        font=("Times", 27))
    movingRaiderTrue()
    movingRaiderWidgit(data)

# everyone
def rolledSevenFunction():
    state.listHand = getListHand(state.myHand)
    if len(state.listHand) > 7:
        moreThanSevenTrue()


def findRaider(data):
    for i in range(len(data.hexObjects)):
        if data.hexObjects[i].raider:
            return i
    return 9

def moveRaider(data, newHex, oldHex=HexBoard.hex10):
    HexBoard.moveRaider(newHex, oldHex)
    init(data)
    return playersOnHex(data, newHex)

def playersOnHex(data, newHex):
    players = []
    if type(newHex) == int:
        hexx = data.hexObjects[newHex]
        v1 = GameBoard.boardVerticies[hexx.v1-1][0]
        v2 = GameBoard.boardVerticies[hexx.v2-1][0]
        v3 = GameBoard.boardVerticies[hexx.v3-1][0]
        v4 = GameBoard.boardVerticies[hexx.v4-1][0]
        v5 = GameBoard.boardVerticies[hexx.v5-1][0]
        v6 = GameBoard.boardVerticies[hexx.v6-1][0]
    else:
        v1 = GameBoard.boardVerticies[newHex.v1[2]-1][0]
        v2 = GameBoard.boardVerticies[newHex.v2[2]-1][0]
        v3 = GameBoard.boardVerticies[newHex.v3[2]-1][0]
        v4 = GameBoard.boardVerticies[newHex.v4[2]-1][0]
        v5 = GameBoard.boardVerticies[newHex.v5[2]-1][0]
        v6 = GameBoard.boardVerticies[newHex.v6[2]-1][0]
    if v1 != 0:
        players.append(v1)
    if v2 != 0:
        players.append(v2)
    if v3 != 0:
        players.append(v3)
    if v4 != 0:
        players.append(v4)
    if v5 != 0:
        players.append(v5)
    if v6 != 0:
        players.append(v6)
    return list(set(players))


def orderPlayers():
    state.orderOfPlay = sorted(state.players)

##############################################################################
# global vars
##############################################################################
buildingHouses = False
buildingCities = False
buildingRoads = False
movingRaider = False
globalTradeCheck = True
globalBoardCheck = True
globalAcceptTradeCheck = True
globalBuildPhaseCheck = True
globalLoginCheck = True
globalRollCheck = True
globalLobbyCheck = True

def resetGlobalLobbyCheck():
    global globalLobbyCheck
    globalLobbyCheck = True

def resetBuildingHouses():
    global buildingHouses
    buildingHouses = False

def resetBuildingCities():
    global buildingCities
    buildingCities = False

def resetBuildingRoads():
    global buildingRoads
    buildingRoads = False

def resetGlobalRoll():
    global globalRollCheck
    globalRollCheck = True

def resetGlobalTrade():
    global globalTradeCheck
    globalTradeCheck = True

def resetGlobalBoard():
    global globalBoardCheck
    globalBoardCheck = True

def resetAcceptWidgit():
    global globalAcceptTradeCheck
    globalAcceptTradeCheck = True

def resetGlobalBuildPhase():
    global globalBuildPhaseCheck
    globalBuildPhaseCheck = True

def inLobbyFalse():
    state.inLobby = False


#############################################################################
def tradeWidgit(data):
    global globalTradeCheck

    if globalTradeCheck:
        globalTradeCheck = False


        def sendReq():
            try:
                message = "trade " #+ request.get() + "\n"
                for key in state.tradeCards:
                    if state.tradeCards[key] != 0:
                        message += str(state.tradeCards[key]) \
                        + " " + key + " "
                for key in state.tradeCards:
                    if state.forCards[key] != 0:
                        message += str(state.forCards[key]) \
                        + " " + key + "\n"
                messageList = message.split(" ")
                if legalTrade(messageList[2], messageList[1]):
                    data.server.send(message.encode())
                    state.tradeCards = {"Wheat":0, "Rock":0, "Brick":0, \
                    "Sheep":0, "Lumber":0}
                    state.forCards = {"Wheat":0, "Rock":0, "Brick":0, \
                    "Sheep":0, "Lumber":0}
                else:
                    state.tradeCards = {"Wheat":0, "Rock":0, "Brick":0, \
                    "Sheep":0, "Lumber":0}
                    state.forCards = {"Wheat":0, "Rock":0, "Brick":0, \
                    "Sheep":0, "Lumber":0}
            except:
                print("None")



###############################################################################
        submit = Button(data.root, text="Request", command=sendReq)
        submit.pack()
        state.submit = submit
        submit.place(x=5*data.width//6, y=data.height//2+10, anchor="center")

        def continueGame():
            state.currentStage += 1
            resetGlobalTrade()
            #tradeReq.destroy()
            submit.destroy()
            continueButton.destroy()
            resetTopTrade.destroy()
            resetBottomTrade.destroy()
            resetTop()
            resetBottom()



        continueButton = Button(data.root, text="Continue",\
                                     command=continueGame)
        continueButton.pack()
        state.continueButton = continueButton
        continueButton.place(x=5*data.width//6, y=3*data.height//6-20,\
         anchor="center")

        def resetTop():
            state.tradeCards = {"Wheat":0, "Rock":0, "Brick":0,\
             "Sheep":0, "Lumber":0}
        def resetBottom():
            state.forCards = {"Wheat":0, "Rock":0, "Brick":0,\
             "Sheep":0, "Lumber":0}

        resetTopTrade = Button(data.root, text="Reset", command=resetTop)
        resetTopTrade.pack()
        state.resetTopTrade = resetTopTrade
        resetTopTrade.place(x=data.width//6, \
            y=data.height//3 + 35, anchor="center")


        resetBottomTrade = Button(data.root, text="Reset", \
            command=resetBottom)
        resetBottomTrade.pack()
        state.resetBottomTrade = resetBottomTrade
        resetBottomTrade.place(x=data.width//6, \
            y=2*data.height//3 - 40, anchor="center")

#############################################################################
def boardWidgit(data):
    global globalBoardCheck

    if globalBoardCheck:
        globalBoardCheck = False

        def continueGame():
            state.currentStage = 1
            state.roll = 0
            resetGlobalBoard()
            continueButton.destroy()
            message = "endTurn " + state.myID + "\n"
            data.server.send(message.encode())
            state.currentPlayer = (state.currentPlayer + 1)\
             % len(state.orderOfPlay)

        continueButton = Button(data.root, text="Finish Turn",\
         command=continueGame)
        continueButton.pack()
        continueButton.place(x=7*data.width//8, \
            y=7*data.height//8, anchor="se")


#############################################################################

def acceptTradeWidgit(data, theirNumber, theirResource, myNumber, myResource, them):
    global globalAcceptTradeCheck

    def updateHandTrade(data, theirNumber, theirResource, myNumber, myResource):
        state.myHand[myResource] -= myNumber
        state.myHand[theirResource] += theirNumber


    if globalAcceptTradeCheck:
        globalAcceptTradeCheck = False

        def acceptTrade(data=data, theirNumber=theirNumber,
                        theirResource=theirResource, myNumber=myNumber,
                        myResource=myResource, them=them):
            tradeStateSwap()
            resetAcceptWidgit()
            acceptButton.destroy()
            declineButton.destroy()
            message = "tradeAccepted " + str(theirNumber) +\
             " " + theirResource + " " + \
                    str(myNumber) + " " + myResource + " " \
                    + them + "\n"
            data.server.send(message.encode())
            updateHandTrade(data, theirNumber, theirResource, \
                myNumber, myResource)
            state.acceptTradeCards = {"Wheat":0, "Rock":0, "Brick":0, \
            "Sheep":0, "Lumber":0}
            state.acceptForCards = {"Wheat":0, "Rock":0, "Brick":0, \
            "Sheep":0, "Lumber":0}

        acceptButton = Button(data.root, text="Accept Trade", \
            command=acceptTrade)
        acceptButton.pack()
        state.acceptButton = acceptButton
        acceptButton.place(x=data.width//2, y=data.height//2, \
            anchor="center")

#############################################################################
        def declineTrade():
            tradeStateSwap()
            acceptButton.destroy()
            resetAcceptWidgit()
            declineButton.destroy()
            message = "cantTrade sorry\n"
            data.server.send(message.encode())
            state.acceptTradeCards = {"Wheat":0, "Rock":0, "Brick":0, \
            "Sheep":0, "Lumber":0}
            state.acceptForCards = {"Wheat":0, "Rock":0, "Brick":0, \
            "Sheep":0, "Lumber":0}

        declineButton = Button(data.root, text="Decline Trade", \
            command=declineTrade)
        declineButton.pack()
        state.declineButton = declineButton
        declineButton.place(x=data.width//2, y=data.height//2+30, \
            anchor="center")


#############################################################################


def buildPhaseWidgits(data):
    global globalBuildPhaseCheck
    if globalBuildPhaseCheck:
        globalBuildPhaseCheck = False

        def buildRoad():
            buildingCities = buildCitiesFalse()
            buildingHouses = buildHousesFalse()
            buildingRoads = buildRoadsTrue()

        buildRoadButton = Button(data.root, text="Build Road", \
            command=buildRoad)
        buildRoadButton.pack()
        buildRoadButton.place(x=data.width//5, y=9*data.height//10, \
            anchor="center")
        state.buildRoadButton = buildRoadButton

        def buildHouse():
            buildingCities = buildCitiesFalse()
            buildingHouses = buildHousesTrue()
            buildingRoads = buildRoadsFalse()

        buildHouseButton = Button(data.root, text="Build House", \
            command=buildHouse)
        buildHouseButton.pack()
        buildHouseButton.place(x=2*data.width//5, y=9*data.height//10, \
            anchor="center")
        state.buildHouseButton = buildHouseButton

        def buildCity():
            buildingCities = buildCitiesTrue()
            buildingHouses = buildHousesFalse()
            buildingRoads = buildRoadsFalse()

        buildCityButton = Button(data.root, text="Build City", \
            command=buildCity)
        buildCityButton.pack()
        buildCityButton.place(x=3*data.width//5, y=9*data.height//10, \
            anchor="center")
        state.buildCityButton = buildCityButton


#############################################################################


        def buyDevCard():
            # check if can buy
            for key in state.developmentCardCost:
                if state.myHand[key] - state.developmentCardCost[key] < 0:
                    return False
            for key in state.developmentCardCost:
                state.myHand[key] -= state.developmentCardCost[key]

            index = random.randint(0,2)
            devCards = ["Knight", "Vp", "RoadBuilding"]
            myDevCard = devCards[index]
            updateDict = {myDevCard:1}
            updateHand(updateDict)
            if myDevCard == "Knight":
                state.totalKnights += 1

        buyDevCardButton = Button(data.root, text="Buy Dev Card", \
            command=buyDevCard)
        buyDevCardButton.pack()
        buyDevCardButton.place(x=4*data.width//5, y=9*data.height//10, \
            anchor="center")
        state.buyDevCardButton = buyDevCardButton


#############################################################################


        def endTurn():
            globalBuildPhaseCheck = True
            resetGlobalBuildPhase()
            buildRoadButton.destroy()
            buildHouseButton.destroy()
            buildCityButton.destroy()
            buyDevCardButton.destroy()
            endTurnButton.destroy()
            resetBuildingCities()
            resetBuildingHouses()
            resetBuildingRoads()
            state.currentStage = 1
            state.roll = 0
            resetGlobalBoard()
            message = "endTurn " + state.myID + "\n"
            data.server.send(message.encode())
            state.currentPlayer = (state.currentPlayer + 1) % \
            len(state.orderOfPlay)



        endTurnButton = Button(data.root, text="End Turn", command=endTurn)
        endTurnButton.pack()
        endTurnButton.place(x=14*data.width//15, y=data.height//2 + 75, \
            anchor="center")
        state.endTurnButton = endTurnButton


#############################################################################

def loginWidgit(data):
    global globalLoginCheck
    if globalLoginCheck:
        globalLoginCheck = False
    # username and password
        usernameLabel = Label(data.root, text="username")
        usernameLabel.pack()
        usernameLabel.place(x=data.width//2-175, y=data.height//2-10)
        username = StringVar()
        usernameEntry = Entry(data.root, textvariable=username)
        usernameEntry.pack()
        usernameEntry.place(x=data.width//2, y=data.height//2, \
            anchor="center")

        passwordLabel = Label(data.root, text="password")
        passwordLabel.pack()
        passwordLabel.place(x=data.width//2-175, y=data.height//2+30)
        password = StringVar()
        passwordEntry = Entry(data.root, textvariable=password, show="*")
        passwordEntry.pack()
        passwordEntry.place(x=data.width//2, y=data.height//2+40, \
            anchor="center")


#############################################################################
        # login button
        def logins():
            if loginCheck(username.get(), password.get()):
                if loginCheck(username.get(), password.get())[0][1]:
                    deck.init()
                    #ez()
                    updateHand({"Wheat":19, "Rock":19, "Brick":19, "Sheep":19, \
                        "Lumber":19})
                    state.currentStage += 1
                    state.username = username.get()
                    state.usernames[state.myID] = username.get()
                    usernameLabel.destroy()
                    passwordLabel.destroy()
                    loginButton.destroy()
                    signupButton.destroy()
                    usernameEntry.destroy()
                    passwordEntry.destroy()
                    orderMessage = "addPlayer " + state.myID + " " + \
                    username.get() + " " +"\n"
                    data.server.send(orderMessage.encode())


        loginButton = Button(data.root, text="Login", borderwidth=0, \
            command=logins)
        loginButton.pack()
        loginButton.place(x=data.width//2, y=data.height//2+70)


#############################################################################
        # sign-up button
        def signup():
            newUser(username.get(), password.get())
            deck.init()
            #ez()
            updateHand({"Wheat":19, "Rock":19, "Brick":19, "Sheep":19, \
                "Lumber":19})
            state.currentStage += 1
            state.username = username.get()
            state.usernames[state.myID] = username.get()
            usernameLabel.destroy()
            passwordLabel.destroy()
            loginButton.destroy()
            signupButton.destroy()
            usernameEntry.destroy()
            passwordEntry.destroy()
            orderMessage = "addPlayer " + state.myID + " " + \
            username.get() + " " +"\n"
            data.server.send(orderMessage.encode())

        signupButton = Button(data.root, text="Sign-Up",command=signup)
        signupButton.pack()
        signupButton.place(x=data.width//2-90, y=data.height//2+70)



#############################################################################


def rollWidgit(data):
    global globalRollCheck
    if globalRollCheck:
        globalRollCheck = False

        def rollDice():
            die1 = rollDie()
            die2 = rollDie()
            state.die1 = die1
            state.die2 = die2
            globalRollCheck = True
            resetGlobalRoll()
            roll = die1 + die2
            state.roll = roll
            rollButton.destroy()
            resources = collectResources(data, roll, state.myColor)
            updateHand(resources)
            message = "rolled " + str(state.roll) + "\n"
            data.server.send(message.encode())
            if roll == 7:
                rolledSevenSwap()

        rollButton = Button(data.root, text="Roll", command=rollDice, \
            borderwidth=0)
        rollButton.pack()
        rollButton.place(x=data.width//2, y=data.height//2 + 100, \
            anchor="center")


#############################################################################

def lobbyWidgits(data):
    global globalLobbyCheck
    if globalLobbyCheck:
        globalLobbyCheck = False

        def startGame():
            state.inLobby = False
            startGameButton.destroy()
            startGameAIButton.destroy()
            message = "start game now \n"
            data.server.send(message.encode())

        def startGameWithAI():
            state.inLobby = False
            startGameButton.destroy()
            startGameAIButton.destroy()
            message = "ai game now \n"
            data.server.send(message.encode())

        startGameButton = Button(data.root, text="Start Game", \
            command=startGame)
        startGameButton.pack()
        startGameButton.place(x=data.width//2 - 50, y=data.height//2, \
            anchor="center")

        startGameAIButton = Button(data.root, text="AI Game", \
            command=startGameWithAI)
        startGameAIButton.pack()
        startGameAIButton.place(x=data.width//2 + 50, y=data.height//2, \
            anchor="center")



#############################################################################


def tradeStateSwap(theirNumber=0, theirResource="", myNumber=0, myResource="", them=""):
    state.trading = not state.trading
    state.theirNumber = theirNumber
    state.theirResource = theirResource
    state.myNumber = myNumber
    state.myResource = myResource
    state.them = them

def buildHousesFalse():
    global buildingHouses
    buildingHouses = False

def buildRoadsFalse():
    global buildingRoads
    buildingRoads = False

def buildCitiesFalse():
    global buildingCities
    buildingCities = False

def buildHousesTrue():
    global buildingHouses
    buildingHouses = True

def buildRoadsTrue():
    global buildingRoads
    buildingRoads = True

def buildCitiesTrue():
    global buildingCities
    buildingCities = True


##############################################################################
# state set-up functions
##############################################################################
def easyTwoPlayer():
    state.buildHouses.append((12,1))
    state.buildHouses.append((20,1))
    state.buildHouses.append((28,2))
    state.buildHouses.append((46,2))

    state.buildRoads.append((12,1))
    state.buildRoads.append((22,1))
    state.buildRoads.append((34,2))
    state.buildRoads.append((65,2))

def easyThreePlayer():
    easyTwoPlayer()
    state.buildHouses.append((9,3))
    state.buildHouses.append((43,3))

    state.buildRoads.append((15,3))
    state.buildRoads.append((55,3))


def easyFourPlayer():
    easyThreePlayer()
    state.buildHouses.append((19,4))
    state.buildHouses.append((40,4))

    state.buildRoads.append((30,4))
    state.buildRoads.append((58,4))
###############################################################################
# state
###############################################################################

class State(object): pass
state = State()
state.myID = ""
state.myColor = 1
state.count = 0
state.buildHouses = []
state.buildRoads = []
state.buildCities = []
state.stages = ["start", "roll", "trade", "buy", "build", "end"]
state.currentStage = 0
state.roll = 0
state.roll1 = 0
state.roll2 = 0
state.myHand = {
        "Wheat":0,
        "Rock":0,
        "Brick":0,
        "Sheep":0,
        "Lumber":0,
        "Knight":0,
        "Vp":0,
        "RoadBuilding":0,
        #"YearOfPlenty":0,
        #"Monoply":0
        }
state.listHand = ["Wheat", "Rock", "Brick", "Sheep", "Lumber"]
state.types =   { "Blank":"white",
                  "Wheat":"yellow",
                  "Rock":"grey",
                  "Brick":"red",
                  "Sheep":"pink",
                  "Lumber": "brown"}
state.colorToResource = { "white":"Blank",
                          "yellow": "Wheat",
                          "grey":"Rock",
                          "red":"Brick",
                          "pink":"Sheep",
                          "brown":"Lumber",
                          "black":"Nothing",
                          }


state.currentPlayer = 0
state.players = []
state.orderOfPlay = ["Player1"]
state.scores = {"Player1":0, "Player2":0, "Player3":0, "Player4":0}
state.myScore = 0

state.roadCost = {"Lumber":1, "Brick":1}
state.houseCost = {"Lumber":1, "Brick":1, "Wheat":1, "Sheep":1}
state.cityCost = {"Wheat":2, "Rock":3}
state.developmentCardCost = {"Wheat":1, "Sheep":1, "Rock":1}

state.tradeTrack = []
state.trading = False
state.myNumber = 0
state.myResource = ""
state.theirNumber = 0
state.theirResource = ""
state.them = ""

state.tradeReq = None
state.submit = None
state.continueButton = None
state.acceptButton = None
state.declineButton = None

state.currRaiderPos = 9
state.nextRaiderPos = 9

state.totalKnights = 0


state.tradeCards = {"Wheat":0, "Rock":0, "Brick":0, "Sheep":0, "Lumber":0}
state.forCards = {"Wheat":0, "Rock":0, "Brick":0, "Sheep":0, "Lumber":0}
state.acceptTradeCards = {"Wheat":0, "Rock":0, "Brick":0, "Sheep":0, \
"Lumber":0}
state.acceptForCards = {"Wheat":0, "Rock":0, "Brick":0, "Sheep":0, \
"Lumber":0}

state.usernames = {}
state.removingCards = False
state.halfFlag = True
state.halfOfSeven = 0

state.gameOver = False
state.winner = ""

state.winCondtion = 10

state.inLobby = True
state.username = "Pablo"
state.usernames = {"Player1":"", "Player2":"", "Player3":"", "Player4":""}
state.longestRoadCheck = {"Player1":False, "Player2":False, \
"Player3":False, "Player4":False}
state.currentLongestRoad = ""
state.currentLongestRoadLength = 0

state.displayRules = False


#############################################################################
# draw helper function
#############################################################################
def drawScoreBoard(canvas, data, state):
    if len(state.players) == 2:
        # player1
        canvas.create_text(300, data.height//17, \
            text=state.usernames["Player1"],
            font=("Times", 40), fill="red")
        canvas.create_text(300, data.height//15 + 20, \
            text="Score: %d" % (state.scores["Player1"]),
            font=("Times", 20), fill="red")
        # player2
        canvas.create_text(450, data.height//17, \
            text=state.usernames["Player2"],
            font=("Times", 40), fill="green")
        canvas.create_text(450, data.height//15 + 20, \
            text="Score: %d" % (state.scores["Player2"]),
            font=("Times", 20), fill="green")
    elif len(state.players) == 3:
        # player1
        canvas.create_text(225, data.height//17, \
            text=state.usernames["Player1"],
            font=("Times", 40), fill="red")
        canvas.create_text(225, data.height//15 + 20, \
            text="Score: %d" % (state.scores["Player1"]),
            font=("Times", 20), fill="red")
        # player2
        canvas.create_text(375, data.height//17, \
            text=state.usernames["Player2"],
            font=("Times", 40), fill="green")
        canvas.create_text(375, data.height//15 + 20, \
            text="Score: %d" % (state.scores["Player2"]),
            font=("Times", 20), fill="green")
        # player3
        canvas.create_text(525, data.height//17, \
            text=state.usernames["Player3"],
            font=("Times", 40), fill="yellow")
        # player4
        canvas.create_text(525, data.height//15 + 20, \
            text="Score: %d" % (state.scores["Player3"]),
            font=("Times", 20), fill="yellow")
    elif len(state.players) == 4:
        # player1
        canvas.create_text(150, data.height//17, \
            text=state.usernames["Player1"],
            font=("Times", 40), fill="red")
        canvas.create_text(150, data.height//15 + 20, \
            text="Score: %d" % (state.scores["Player1"]),
            font=("Times", 20), fill="red")
        # player2
        canvas.create_text(300, data.height//17, \
            text=state.usernames["Player2"],
            font=("Times", 40), fill="green")
        canvas.create_text(300, data.height//15 + 20, \
            text="Score: %d" % (state.scores["Player2"]),
            font=("Times", 20), fill="green")
        # player3
        canvas.create_text(450, data.height//17, \
            text=state.usernames["Player3"],
            font=("Times", 40), fill="yellow")
        canvas.create_text(450, data.height//15 + 20, \
            text="Score: %d" % (state.scores["Player3"]),
            font=("Times", 20), fill="yellow")
        # player4
        canvas.create_text(600, data.height//17, \
            text=state.usernames["Player4"],
            font=("Times", 40), fill="white")
        canvas.create_text(600, data.height//15 + 20, \
            text="Score: %d" % (state.scores["Player4"]),
            font=("Times", 20), fill="white")

#############################################################################

def drawDieRoll(canvas, data, state, x, y):
    index = random.randint(0,5)
    canvas.create_image(x, y, image=data.allDie[index])

#############################################################################

def drawHandWithPictures(canvas, data, state, x, y, xShift, yShift):
    index = 0
    for key in state.myHand:
        indecie = 0
        if key == "Field":
            indecie = 0
        elif key == "Lumber":
            indecie = 1
        elif key == "Brick":
            indecie = 2
        elif key == "Rock":
            indecie = 3
        elif key == "Wheat":
            indecie = 4
        elif key == "Vp":
            indecie = 5
        elif key == "RoadBuilding":
            indecie = 6
        elif key == "Knight":
            indecie = 7
        horShift = index * xShift
        vertShift = index * yShift
        # vertShift
        canvas.create_image(x + horShift, y + vertShift,
                image=data.allCards[indecie])
        canvas.create_text(x+horShift, y+vertShift,
                            text="%d" % (state.myHand[key]), \
                            font=("Times", 30))
        index += 1

#############################################################################
def drawHand(canvas, data, state, x, y, shift):
    canvas.create_text(x,y,text="My Hand:")
    index = 1
    for key in state.myHand:
        place = index * shift
        canvas.create_text(x, y+place, \
            text="%s: %d" % (key, state.myHand[key]))
        index += 1

def drawHandWithValues(canvas, data, state, x, y, xShift, yShift, d):
    startval ={"Wheat":0,"Rock":0,"Brick":0,"Sheep":0,"Lumber":0}
    for key in d:
        startval[key] += d[key]
    index = 0
    for key in startval:
        indecie = 0
        if key == "Sheep":
            indecie = 0
        elif key == "Lumber":
            indecie = 1
        elif key == "Brick":
            indecie = 2
        elif key == "Rock":
            indecie = 3
        elif key == "Wheat":
            indecie = 4
        horShift = index * xShift
        vertShift = index * yShift
        canvas.create_image(x + horShift, y + vertShift,
                image=data.allCards[indecie])
        canvas.create_text(x+horShift, y+vertShift,
                            text="%d" % (startval[key]), \
                            font=("Times", 30))
        index += 1


def drawBoard(canvas, data, state):
    canvas.create_image(data.width//2, data.height//2, image=data.water)
    drawHexes(canvas, data, data.allHexes, data.hexColors)
    drawRoads(canvas, state, data)
    drawHouses(canvas, state, data)
    drawCities(canvas, state, data)
    drawHandWithPictures(canvas, data, state, 50, 75, 0, 75)
    drawScoreBoard(canvas, data, state)
##############################################################################
# draw game states
##############################################################################

def drawWelcome(canvas, data, state):
    canvas.create_image(data.width//2, data.height//2+100, \
        image=data.loginBackground)
    loginWidgit(data)

def drawRollStage(canvas, data, state):
    canvas.create_image(data.width//2, data.height//2, \
        image=data.table)
    if state.roll == 0:
        drawDieRoll(canvas, data, state, data.width//2-100, data.height//2)
        drawDieRoll(canvas, data, state, data.width//2+100, data.height//2)
        rollWidgit(data)
    elif state.roll != 0:
        canvas.create_image(data.width//2, data.height//4, \
            image=data.cToContinue)

        canvas.create_image(data.width//2-100, data.height//2, \
            image=data.allDie[state.die1-1])
        canvas.create_image(data.width//2+100, data.height//2, \
            image=data.allDie[state.die2-1])

        thisRoll = collectResources(data, state.roll, state.myColor)

        if thisRoll == {}:
            canvas.create_image(data.width//2, 3*data.height//4, \
                image=data.noCollect)

        else:
            drawHandWithValues(canvas, data, state, 215, 600, 75, 0, thisRoll)


###############################################################################
def drawWait(canvas, data, state):
    drawBoard(canvas, data, state)

    canvas.create_text(data.width//2 + 30, 9*data.height//10, \
        text="please wait",
             font=("Times",50), fill="white")


def drawTradeStage(canvas, data, state):
    # draw background
    canvas.create_image(data.width//2, data.height//2,image=data.offerTradeImg)
    # draw instructions
    canvas.create_image(data.width//2, 100, image=data.clickToIncrease)

    # draw top
    canvas.create_image(data.width//2, 200, image=data.tradeText)
    drawHandWithValues(canvas, data, state, 215, 280, 75, 0, state.tradeCards)
    # draw middle
    canvas.create_image(data.width//2, 370, image=data.forText)
    drawHandWithValues(canvas, data, state, 215, 450, 75, 0, state.forCards)
    # draw bottom
    # find the hand dictionary
    myCurrentHand = {}
    for key in state.myHand:
        if key != "Vp" and key != "Knight" and key != "RoadBuilding":
            myCurrentHand[key] = state.myHand[key]

    canvas.create_image(data.width//2, 540, image=data.myHandText)
    drawHandWithValues(canvas, data, state, 215, 620, 75, 0, myCurrentHand)

    tradeWidgit(data)

###############################################################################


def drawTradeScreen(canvas, data, state):
    # draw background
    canvas.create_image(data.width//2, data.height//2, \
        image=data.table)
    # draw hand
    drawHandWithValues(canvas, data, state, 215, 200, 75, 0, \
        state.acceptTradeCards)
    drawHandWithValues(canvas, data, state, 215, 620, 75, 0, \
        state.acceptForCards)
    drawHandWithPictures(canvas, data, state, 50, 100, 0, 75)

    canvas.create_text(data.width//2, data.height//6,
            text="Trade", anchor="center", font=(("ms Serif", 30)))
    canvas.create_text(data.width//2, 4*data.height//6, text="For", \
        anchor="center", font=(("ms Serif", 30)))
    acceptTradeWidgit(data, state.theirNumber, state.theirResource, \
        state.myNumber, state.myResource, state.them)

###############################################################################

def drawBuild(canvas, data, state):
    drawBoard(canvas, data, state)

    buildPhaseWidgits(data)
    if buildingHouses:
        canvas.create_text(data.width//2, 8.5*data.height//10,
                            text="Build Houses")
    elif buildingCities:
        canvas.create_text(data.width//2, 8.5*data.height//10,
                            text="Build Cities")
    elif buildingRoads:
        canvas.create_text(data.width//2, 8.5*data.height//10,
                            text="Build Roads")


###############################################################################


def drawRolledSeven(canvas, data, state):
    drawBoard(canvas, data, state)
    # draw announcement on top
    canvas.create_text(data.width//2, data.height//7.5, text="7 Rolled",
        font=("Times", 27))
    # draw whats in hand left of screen
    # check for move than 7
    if moreThanSeven:
        removeCards(canvas, data, state)
    # if its my turn, move the raider
    elif state.orderOfPlay[state.currentPlayer] == state.myID \
    and not moreThanSeven:
        drawMoveRaider(canvas, data, state)

    # get out of the screen
    else:
        rolledSevenSwap()

###############################################################################

def drawLobby(canvas, data, state):
    # background
    canvas.create_image(data.width//2, data.height//2+20, image=data.lobby)
    if state.myID == "Player1":
        lobbyWidgits(data)
    for key in state.usernames:
        if key == "Player1":
            canvas.create_text(data.width//4, data.height//4,
                                text=state.usernames["Player1"], \
                                fill="red", font=("Times",60))
        if key == "Player2":
            canvas.create_text(3*data.width//4, data.height//4,
                                text=state.usernames["Player2"], \
                                fill="green", font=("Times",60))
        if key == "Player3":
            canvas.create_text(data.width//4, 3*data.height//4,
                                text=state.usernames["Player3"], \
                                fill="yellow", font=("Times",60))
        if key == "Player4":
            canvas.create_text(3*data.width//4, 3*data.height//4,
                                text=state.usernames["Player4"], \
                                fill="white", font=("Times",60))


###############################################################################


def drawEndGame(canvas, data, state):
    if state.scores[state.myID] >= state.winCondtion:
        canvas.create_image(data.width//2, data.height//2, \
            image=data.youWonImage)
    else:
        canvas.create_image(data.width//2, data.height//2, \
            image=data.youLostImage)
        canvas.create_text(data.width//2, data.height//2, \
            text=state.usernames[state.winner] + " Won", \
            font=(("ms Serif", 30)))

    if state.orderOfPlay[state.currentPlayer%len(state.orderOfPlay)] == \
                                                                state.myID:
        state.buildRoadButton.destroy()
        state.buildHouseButton.destroy()
        state.buildCityButton.destroy()
        state.buyDevCardButton.destroy()
        state.endTurnButton.destroy()


def drawRules(canvas, data, state):
    canvas.create_image(data.width//2, data.height//2, image=data.rules)






###############################################################################
# data init set up
###############################################################################

def getSides(data):
    # make board look best
    wFactor = data.width//15
    hFactor = data.height//24
    sides = []
    for i in range(len(GameBoard.boardSides)):
        side = []
        for j in range(len(GameBoard.boardSides[0][1])):
            if j % 2 == 0:
                side.append(GameBoard.boardSides[i][1][j] * wFactor)
            elif j % 2 == 1:
                side.append(GameBoard.boardSides[i][1][j] * hFactor)
        sides.append(side)
    return sides

def getVerticies(data):
    wFactor = data.width//15
    hFactor = data.height//24
    verticies = []
    for i in range(len(GameBoard.boardVerticies)):
        verticie = []
        for j in range(len(GameBoard.boardVerticies[0][1])):
            if j % 2 == 0:
                verticie.append(GameBoard.boardVerticies[i][1][j] * wFactor)
            elif j % 2 == 1:
                verticie.append(GameBoard.boardVerticies[i][1][j] * hFactor)
        verticies.append(verticie)
    return verticies

def cleanHex(data, thisHex):
    wFactor = data.width//15
    hFactor = data.height//24
    x1 = thisHex.v1[1][0] * wFactor
    y1 = thisHex.v1[1][1] * hFactor
    x2 = thisHex.v2[1][0] * wFactor
    y2 = thisHex.v2[1][1] * hFactor
    x3 = thisHex.v3[1][0] * wFactor
    y3 = thisHex.v3[1][1] * hFactor
    x4 = thisHex.v4[1][0] * wFactor
    y4 = thisHex.v4[1][1] * hFactor
    x5 = thisHex.v5[1][0] * wFactor
    y5 = thisHex.v5[1][1] * hFactor
    x6 = thisHex.v6[1][0] * wFactor
    y6 = thisHex.v6[1][1] * hFactor
    return (x1,y1,x2,y2,x3,y3,x4,y4,x5,y5,x6,y6)

###############################################################################
# Change Board Functions
###############################################################################

def changeHexType(data, n, newType):
    HexBoard.changeType(data.hexObjects[n-1], state.types[newType])
    init(data)

def drawRoad(canvas, index, side, myColor):
    GameBoard.updateSide(index, myColor)
    color = "black"
    if GameBoard.boardSides[index][2] == 1:
        color = "red"
    elif GameBoard.boardSides[index][2] == 2:
        color = "green"
    elif GameBoard.boardSides[index][2] == 3:
        color = "yellow"
    elif GameBoard.boardSides[index][2] == 4:
        color = "white"
    canvas.create_line(side, fill=color, width=10)

def drawHouse(canvas, index, verticie, data, myColor):
    GameBoard.updateVerticie(index, myColor)
    r = data.width // 50
    cx = verticie[0]
    cy = verticie[1]
    color = "black"
    if GameBoard.boardVerticies[index][0] == 1:
        color = "red"
    elif GameBoard.boardVerticies[index][0] == 2:
        color = "green"
    elif GameBoard.boardVerticies[index][0] == 3:
        color = "yellow"
    elif GameBoard.boardVerticies[index][0] == 4:
        color = "white"
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, width=1)
    updateScore(data)

def drawCity(canvas, index, verticie, data, myColor):
    r = data.width//45
    cx = verticie[0]
    cy = verticie[1]
    color = "black"
    houseColor = GameBoard.boardVerticies[index][0]
    if houseColor == 1:
        color = "Red"
    elif houseColor == 2:
        color = "Green"
    elif houseColor == 3:
        color = "yellow"
    elif houseColor == 4:
        color = "White"
    canvas.create_rectangle(cx-r, cy-r, cx+r, cy+r, fill=color, width=1)
    updateScore(data)

def drawHexes(canvas, data, hexes, colors):
    for i in range(len(hexes)):
        color = colors[i]
        canvas.create_polygon(hexes[i], fill=color, width=2, outline="black")
        cx = (hexes[i][0]+hexes[i][2]+hexes[i][4]+hexes[i][6]+\
            hexes[i][8]+hexes[i][10])//6
        cy = (hexes[i][1]+hexes[i][3]+hexes[i][5]+hexes[i][7]+\
            hexes[i][9]+hexes[i][11])//6
        # draw based on type
        if data.hexObjects[i].attr == "black":
            canvas.create_image(cx, cy, image=data.sandPiece)
        if data.hexObjects[i].attr == "pink":
            canvas.create_image(cx, cy, image=data.allPieces[0])
        if data.hexObjects[i].attr == "brown":
            canvas.create_image(cx, cy, image=data.allPieces[1])
        if data.hexObjects[i].attr == "red":
            canvas.create_image(cx, cy, image=data.allPieces[2])
        if data.hexObjects[i].attr == "grey":
            canvas.create_image(cx, cy, image=data.allPieces[3])
        if data.hexObjects[i].attr == "yellow":
            canvas.create_image(cx, cy, image=data.allPieces[4])


        if data.hexObjects[i] != 0 and data.hexObjects[i].attr != "black":
            canvas.create_image(cx,cy,\
                image=data.allTiles[data.hexObjects[i].roll-2])
        if data.hexObjects[i].raider == True:
            canvas.create_image(cx, cy, image=data.raiderCard)

###############################################################################

def drawHouses(canvas, state, data):
    for i in range(len(state.buildHouses)):
        drawHouse(canvas, state.buildHouses[i][0], \
            data.verticies[state.buildHouses[i][0]], data,
                          state.buildHouses[i][1])

def drawRoads(canvas, state, data):
    for i in range(len(state.buildRoads)):
        drawRoad(canvas, state.buildRoads[i][0], \
            data.sides[state.buildRoads[i][0]],
                 state.buildRoads[i][1])

def drawCities(canvas, state, data):
    for i in range(len(state.buildCities)):
        drawCity(canvas, state.buildCities[i][0], \
            data.verticies[state.buildCities[i][0]],
                data, state.buildHouses[i][1])




###############################################################################
# Hand Functions
###############################################################################

def updateHand(d):
    for key in d:
        state.myHand[key] += d[key]


def collectResources(data, roll, myColor):
    collect = {}
    # go thorugh hexes and see if any of
    # my color is on an edge and add the resource
    # of the hex I am on if I am on one
    for i in range(len(data.hexObjects)):
        if roll == data.hexObjects[i].roll:
            resource = state.colorToResource[data.hexObjects[i].attr]
            hexx = data.hexObjects[i]
            if myColor == data.hexObjects[i].v1[0]:
                collect[resource] = collect.get(resource, 0) + 1
                if (hexx.v1[2]-1, myColor) in state.buildCities:
                    collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v2[0]:
                collect[resource] = collect.get(resource, 0) + 1
                if (hexx.v2[2]-1, myColor) in state.buildCities:
                    collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v3[0]:
                collect[resource] = collect.get(resource, 0) + 1
                if (hexx.v3[2]-1, myColor) in state.buildCities:
                    collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v4[0]:
                collect[resource] = collect.get(resource, 0) + 1
                if (hexx.v4[2]-1, myColor) in state.buildCities:
                    collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v5[0]:
                collect[resource] = collect.get(resource, 0) + 1
                if (hexx.v5[2]-1, myColor) in state.buildCities:
                    collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v6[0]:
                collect[resource] = collect.get(resource, 0) + 1
                if (hexx.v6[2]-1, myColor) in state.buildCities:
                    collect[resource] = collect.get(resource, 0) + 1
    return collect

def buyResource(myHand, resource):
    for key in resource:
        if not (myHand[key] >= resource[key]):
            return None
        myHand[key] -= resource[key]
        deck.deck.resourceDeck[key] += resource[key]

def getListHand(myHand):
    handList = []
    for key in myHand:
        for i in range(myHand[key]):
            handList.append(key)
    return handList

def legalTrade(myResource, myNumber):
    return state.myHand[myResource] >= int(myNumber)




###############################################################################
# init
###############################################################################
def init(data):

    data.messageToSend = ""
    data.hexMessage = ""
    data.raodMessage = ""
    data.houseMessage = ""

    data.sides = getSides(data)
    data.verticies = getVerticies(data)

    #data.myTurn = isMyTurn()

    data.hex1 = cleanHex(data, HexBoard.hex1)
    data.hex2 = cleanHex(data, HexBoard.hex2)
    data.hex3 = cleanHex(data, HexBoard.hex3)
    data.hex4 = cleanHex(data, HexBoard.hex4)
    data.hex5 = cleanHex(data, HexBoard.hex5)
    data.hex6 = cleanHex(data, HexBoard.hex6)
    data.hex7 = cleanHex(data, HexBoard.hex7)
    data.hex8 = cleanHex(data, HexBoard.hex8)
    data.hex9 = cleanHex(data, HexBoard.hex9)
    data.hex10 = cleanHex(data, HexBoard.hex10)
    data.hex11 = cleanHex(data, HexBoard.hex11)
    data.hex12 = cleanHex(data, HexBoard.hex12)
    data.hex13 = cleanHex(data, HexBoard.hex13)
    data.hex14 = cleanHex(data, HexBoard.hex14)
    data.hex15 = cleanHex(data, HexBoard.hex15)
    data.hex16 = cleanHex(data, HexBoard.hex16)
    data.hex17 = cleanHex(data, HexBoard.hex17)
    data.hex18 = cleanHex(data, HexBoard.hex18)
    data.hex19 = cleanHex(data, HexBoard.hex19)
    data.allHexes = [data.hex1, data.hex2, data.hex3, data.hex4, data.hex5,
                     data.hex6, data.hex7, data.hex8, data.hex9, data.hex10,
                     data.hex11, data.hex12, data.hex13, data.hex14,
                     data.hex15, data.hex16, data.hex17, data.hex18,
                     data.hex19]
    data.hexColors = [HexBoard.hex1.attr, HexBoard.hex2.attr,
                      HexBoard.hex3.attr, HexBoard.hex4.attr,
                      HexBoard.hex5.attr, HexBoard.hex6.attr,
                      HexBoard.hex7.attr, HexBoard.hex8.attr,
                      HexBoard.hex9.attr, HexBoard.hex10.attr,
                      HexBoard.hex11.attr, HexBoard.hex12.attr,
                      HexBoard.hex13.attr, HexBoard.hex14.attr,
                      HexBoard.hex15.attr, HexBoard.hex16.attr,
                      HexBoard.hex17.attr, HexBoard.hex18.attr,
                      HexBoard.hex19.attr]
    data.hexObjects = [ HexBoard.hex1, HexBoard.hex2,
                        HexBoard.hex3, HexBoard.hex4,
                        HexBoard.hex5, HexBoard.hex6,
                        HexBoard.hex7, HexBoard.hex8,
                        HexBoard.hex9, HexBoard.hex10,
                        HexBoard.hex11, HexBoard.hex12,
                        HexBoard.hex13, HexBoard.hex14,
                        HexBoard.hex15, HexBoard.hex16,
                        HexBoard.hex17, HexBoard.hex18,
                        HexBoard.hex19]




###############################################################################
# mouse pressed
###############################################################################

def mousePressed(event, data):
    # for the house building

# all math and absolute value type things are finding the bounds on
# clicks

    x = event.x
    y = event.y
    if buildingHouses:
        for i in range(len(data.verticies)):
            xCheck = abs(event.x - data.verticies[i][0])
            yCheck = abs(event.y - data.verticies[i][1])
            if xCheck <= 10 and yCheck <= 10:
                if GameBoard.boardVerticies[i][0] == 0:
                    house = i
                    if not gameLegalHouse(house, state.myColor):
                        return False
                    for key in state.houseCost:
                        if state.myHand[key] - state.houseCost[key] < 0:
                            return False
                    for key in state.houseCost:
                        state.myHand[key] -= state.houseCost[key]
                    message = "buildHouse" + " " + str(i) + " " + \
                    str(state.myColor) + "\n"
                    data.server.send(message.encode())
                    state.buildHouses.append((i, state.myColor))

###############################################################################
    # for the road building
    # just checking bounds on building roads in the right place
    if buildingRoads:
        for i in range(len(data.sides)):
            x = event.x
            y = event.y
            myXDiff = abs(x - data.sides[i][2])
            xDiff = abs(data.sides[i][0] - data.sides[i][2])
            myYDiff = abs(y - data.sides[i][3])
            yDiff = abs(data.sides[i][1] - data.sides[i][3])
            bigX = x - data.sides[i][2]
            bigY = y - data.sides[i][3]
            if xDiff == 0:
                if myXDiff < 10  and myYDiff < yDiff:
                    if GameBoard.boardSides[i][2] == 0:
                        road = i
                        if not legalRoad(road, state.myColor):
                            return False
                        index = GameBoard.boardSides[i][0]-1
                        for key in state.roadCost:
                            if state.myHand[key] - state.roadCost[key] < 0:
                                return False
                        for key in state.roadCost:
                            state.myHand[key] -= state.roadCost[key]
                        message = "buildRoad" + " " + str(road) + " " + \
                        str(state.myColor) + "\n"
                        data.server.send(message.encode())
                        state.buildRoads.append((i, state.myColor))

            elif xDiff > 0 and myXDiff < xDiff and myYDiff + 10 < yDiff:
                index = i
                if bigX > 0:
                    index += 1
                if GameBoard.boardSides[index][2] == 0:
                    road = index
                    if not legalRoad(road, state.myColor):
                        return False
                    newIndex = GameBoard.boardSides[index][0]-1
                    for key in state.roadCost:
                        if state.myHand[key] - state.roadCost[key] < 0:
                            return False
                    for key in state.roadCost:
                        state.myHand[key] -= state.roadCost[key]
                    message = "buildRoad" + " " + str(newIndex) + " " + \
                    str(state.myColor) + "\n"
                    data.server.send(message.encode())
                    state.buildRoads.append((newIndex, state.myColor))


###############################################################################

    if buildingCities:
        for i in range(len(data.verticies)):
            xCheck = abs(event.x - data.verticies[i][0])
            yCheck = abs(event.y - data.verticies[i][1])
            if xCheck <= 10 and yCheck <= 10:
                # make sure no house is there
                if GameBoard.boardVerticies[i][0] == state.myColor \
                and (i, state.myColor) not in state.buildCities:
                    city = i
                    for key in state.cityCost:
                        if state.myHand[key] - state.cityCost[key] < 0:
                            return False
                    for key in state.cityCost:
                        state.myHand[key] -= state.cityCost[key]
                    message = "buildCity " + str(i) + " " + \
                    str(state.myColor) + "\n"
                    data.server.send(message.encode())
                    state.buildCities.append((i, state.myColor))
                    # send message to everyone to update their board


###############################################################################
    if movingRaider:
        for i in range(len(data.allHexes)):
            myXDiff = abs(data.allHexes[i][4] - x)
            xDiff = abs(data.allHexes[i][4] - data.allHexes[i][0])
            myYDiff = abs(data.allHexes[i][7] - y)
            yDiff = abs(data.allHexes[i][7] - data.allHexes[i][5])
            bigX = data.allHexes[i][4] - x
            if myXDiff < xDiff and myYDiff < yDiff and bigX >= 0:
                currRaiderPos = data.hexObjects[findRaider(data)]
                nextRaiderPos = data.hexObjects[i]
                state.currRaiderPos = currRaiderPos
                state.nextRaiderPos = nextRaiderPos
                moveRaider(data, nextRaiderPos, currRaiderPos)

###############################################################################

    if state.stages[state.currentStage] == "buy":
        xDiff = x - 25
        knightDiff = y - 6*75 + 75//2
        roadBuildingDiff = y - 8*75 + 75//2
        if xDiff >= 0 and knightDiff >= 0:
            if knightDiff <= 75 and xDiff < 50:
                if state.myHand["Knight"] > 0:
                    drawMoveRaider(data.canvas, data, state)
                    updateHand({"Knight":-1})


        if xDiff >= 0 and roadBuildingDiff >= 0:
            if roadBuildingDiff <= 75 and xDiff < 50:
                if state.myHand["RoadBuilding"] > 0:
                    updateHand({"Lumber":2, "Brick":2})
                    updateHand({"RoadBuilding":-1})

###############################################################################

    if state.stages[state.currentStage] == "trade":
        if 190 <= x and x <= 241:
            # bottom
            if 412 <= y and y <= 488:
                state.forCards["Wheat"] += 1
            elif 242 <= y and y <= 318:
                state.tradeCards["Wheat"] += 1
        if 266 <= x and x <= 316:
            # bottom
            if 412 <= y and y <= 488:
                state.forCards["Rock"] += 1
            elif 242 <= y and y <= 318:
                state.tradeCards["Rock"] += 1
        if 341 <= x and x <= 391:
            # bottom
            if 412 <= y and y <= 488:
                state.forCards["Brick"] += 1
            elif 242 <= y and y <= 318:
                state.tradeCards["Brick"] += 1
        if 416 <= x and x <= 466:
            # bottom
            if 412 <= y and y <= 488:
                state.forCards["Sheep"] += 1
            elif 242 <= y and y <= 318:
                state.tradeCards["Sheep"] += 1
        if 491 <= x and x <= 541:
            # bottom
            if 412 <= y and y <= 488:
                state.forCards["Lumber"] += 1
            elif 242 <= y and y <= 318:
                state.tradeCards["Lumber"] += 1


###############################################################################

    if state.removingCards:
        if 190 <= x and x <= 241:
            if 242 <= y and y <= 318:
                if state.myHand["Wheat"] > 0:
                    state.myHand["Wheat"] -= 1
        if 266 <= x and x <= 316:
            if 242 <= y and y <= 318:
                if state.myHand["Rock"] > 0:
                    state.myHand["Rock"] -= 1
        if 341 <= x and x <= 391:
            if 242 <= y and y <= 318:
                if state.myHand["Brick"] > 0:
                    state.myHand["Brick"] -= 1
        if 416 <= x and x <= 466:
            if 242 <= y and y <= 318:
                if state.myHand["Sheep"] > 0:
                    state.myHand["Sheep"] -= 1
        if 491 <= x and x <= 541:
            if 242 <= y and y <= 318:
                if state.myHand["Lumber"] > 0:
                    state.myHand["Lumber"] -= 1



###############################################################################
# key pressed
###############################################################################

def keyPressed(event, data):

        # ROLL STAGE

    if state.stages[state.currentStage] == "roll":
        if event.keysym == "c" and state.roll != 0:
            state.currentStage += 1


     ##############################################################
                          # anytime
      ###########################################################
    if event.keysym == "i" \
    and state.orderOfPlay[state.currentPlayer%len(state.orderOfPlay)] != state.myID\
    and state.stages[state.currentStage] != "start"\
    and not state.inLobby:
        state.displayRules = not state.displayRules



def timerFired(data):
    # check for player with longest road
    # receive and execute messsges
    while (serverMsg.qsize() > 0):
        msg = serverMsg.get(False)
        msg = msg.split()
        player = msg[0]
        command = msg[1]

        if player == "myIDis":
            state.myID = command
            state.players.append(state.myID)
            if command == "Player1":
                state.myColor = 1
            elif command == "Player2":
                state.myColor = 2
            elif command == "Player3":
                state.myColor = 3
            elif command == "Player4":
                state.myColor = 4

        elif command == "changeHex":
            changeHexType(data, int(msg[2]), msg[3])


        elif command == "buildRoad":
            road = int(msg[2])
            color = int(msg[3])
            state.buildRoads.append((road,color))

        elif command == "buildHouse":
            house = int(msg[2])
            color = int(msg[3])
            state.buildHouses.append((house, color))

        elif command == "buildCity":
            city = int(msg[2])
            color = int(msg[3])
            state.buildCities.append((city, color))

        elif command == "rolled":
            roll = int(msg[2])
            resources = collectResources(data, roll, state.myColor)
            updateHand(resources)
            if roll == 7:
                rolledSevenSwap()

        elif command == "addPlayer":
            if msg[2] in state.players:
                continue
            state.players.append(msg[2])
            username = msg[3]
            orderPlayers()
            if len(state.players) == 2:
                easyTwoPlayer()
            elif len(state.players) == 3:
                easyThreePlayer()
            elif len(state.players) == 4:
                easyFourPlayer()
            state.usernames[msg[2]] = username

###############################################################################
        elif command == "endTurn":
            lastPlayer = msg[2]
            nextPlayer = (state.orderOfPlay.index(lastPlayer) + 1) \
            % len(state.orderOfPlay)
            state.currentPlayer = nextPlayer

        elif command == "trade":
            theirNumber = int(msg[2])
            theirResource = msg[3]
            myNumber = int(msg[4])
            myResource = msg[5]
            them = player
            state.acceptTradeCards[theirResource] = theirNumber
            state.acceptForCards[myResource] = myNumber
            if state.myHand[myResource] < myNumber:
                sorryMessage = "cantTrade sorry\n"
                data.server.send(sorryMessage.encode())
            else:
                tradeStateSwap(theirNumber, theirResource, myNumber, \
                    myResource, them)

        elif command == "cantTrade":
            state.tradeTrack.append(0)
            if len(state.tradeTrack) == len(state.players)-1:
                state.currentStage += 1
                resetAcceptWidgit()
                state.submit.destroy()
                state.continueButton.destroy()
                resetGlobalTrade()
                state.resetTopTrade.destroy()
                state.resetBottomTrade.destroy()

###############################################################################
        elif command == "tradeAccepted":
            myResource = msg[3]
            myNumber = int(msg[2])
            theirResource = msg[5]
            theirNumber = int(msg[4])
            me = msg[6]
            if me == state.myID:
                state.myHand[theirResource] += theirNumber
                state.myHand[myResource] -= myNumber
                state.currentStage += 1
                state.submit.destroy()
                state.continueButton.destroy()
                state.resetTopTrade.destroy()
                state.resetBottomTrade.destroy()
                resetGlobalTrade()
                resetAcceptWidgit()

            elif state.trading:
                tradeStateSwap()
                resetAcceptWidgit()
                state.acceptButton.destroy()
                state.declineButton.destroy()


###############################################################################
        elif command == "Raider":
            currPos = msg[2]
            nextPos = msg[3]
            moveRaider(data, eval(nextPos), data.hexObjects[findRaider(data)])

        elif command == "steal":
            newPlayer = msg[2]
            if newPlayer == state.myID:
                state.listHand = getListHand(state.myHand)
                if len(state.listHand) != 0:
                    resource = ""
                    for key in state.myHand:
                        if state.myHand[key] != 0:
                            resource = key
                            removeDict = {resource:-1}
                            updateHand(removeDict)
                            message = "add " + player + " " + \
                            resource + "\n"
                            data.server.send(message.encode())
                            break

        elif command == "add":
            newPlayer = msg[2]
            resource  = msg[3]
            if newPlayer == state.myID:
                resourceAdd = {resource:1}
                updateHand(resourceAdd)

        elif command == "gameOver":
            playerScore = int(msg[2])
            state.gameOver = True
            if playerScore == 3:
                state.winner = player

        elif command == "start":
            state.inLobby == False
            inLobbyFalse()

        elif command == "ai":
            state.inLobby == False
            inLobbyFalse()





        serverMsg.task_done()






def redrawAll(canvas, data):
    checkGameOver(data)
    if state.inLobby and state.stages[state.currentStage] != "start":
        drawLobby(canvas, data, state)
    elif state.gameOver:
        drawEndGame(canvas, data, state)
    elif rolledSeven:
        drawRolledSeven(canvas, data, state)
    elif state.trading:
        drawTradeScreen(canvas, data, state)
    elif state.stages[state.currentStage] == "start":
        drawWelcome(canvas, data, state)
    elif state.orderOfPlay[state.currentPlayer%len(state.orderOfPlay)] \
    != state.myID and not state.trading:
        drawWait(canvas, data, state)
    elif state.stages[state.currentStage] == "roll" and not state.trading:
        drawRollStage(canvas, data, state)
    elif state.stages[state.currentStage] == "trade":
        drawTradeStage(canvas, data, state)
    else:
        drawBuild(canvas, data, state)
    if state.displayRules and state.stages[state.currentStage] != "start":
        drawRules(canvas, data, state)

####################################
# use the run function as-is
####################################

def run(width=300, height=300, serverMsg=None, server=None):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        # canvas.create_rectangle(0, 0, data.width, data.height,
        #                         fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    # SOCKETS SERVER EDITS
    data.server = server
    data.serverMsg = serverMsg
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # addition
    state = Struct()
    state.count = 0
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    data.root = root
    data.canvas = canvas
    ###########################
    # PICTURES
    ###########################
    # background images
    ###############################################################################
    loginBackground = PhotoImage(file="photos/images/cBG.gif")
    data.loginBackground = loginBackground

    table = PhotoImage(file="photos/images/background/Roll_Table.gif")
    data.table = table

    water = PhotoImage(file="photos/images/background/Game_Board.gif")
    data.water = water

    lobby = PhotoImage(file="photos/images/background/myLobby.gif")
    data.lobby = lobby

    offerTradeImg = PhotoImage(file="photos/images/background/\
Offer_Trade.gif")
    data.offerTradeImg = offerTradeImg

    youWonImage = PhotoImage(file="photos/images/background/You_Won.gif")
    data.youWonImage = youWonImage

    youLostImage = PhotoImage(file="photos/images/background/You_Lose.gif")
    data.youLostImage = youLostImage

    rules = PhotoImage(file="photos/images/background/rules.gif")
    data.rules = rules




###############################################################################
    # pieces
    fieldPiece = PhotoImage(file="photos/images/catanPieces/fieldPiece.gif")
    data.fieldPiece = fieldPiece
    forestPiece = PhotoImage(file="photos/images/catanPieces/\
forestPiece.gif")
    data.forestPiece = forestPiece
    brickPiece = PhotoImage(file="photos/images/catanPieces/brickPiece.gif")
    data.brickPiece = brickPiece
    rockPiece = PhotoImage(file="photos/images/catanPieces/rockPiece.gif")
    data.rockPiece = rockPiece
    wheatPiece = PhotoImage(file="photos/images/catanPieces/wheatPiece.gif")
    data.wheatPiece = wheatPiece
    sandPiece = PhotoImage(file="photos/images/newCatanPieces/\
sandPiece.gif")
    data.sandPiece = sandPiece

    data.allPieces = [data.fieldPiece, data.forestPiece, data.brickPiece,
                      data.rockPiece, data.wheatPiece]

###############################################################################
    # cards
    raiderCard = PhotoImage(file="photos/images/catanPieces/raiderCard.gif")
    data.raiderCard = raiderCard
    fieldCard = PhotoImage(file="photos/images/catanPieces/fieldCard.gif")
    data.fieldCard = fieldCard
    forestCard = PhotoImage(file="photos/images/catanPieces/forestCard.gif")
    data.forestCard = forestCard
    brickCard = PhotoImage(file="photos/images/catanPieces/brickCard.gif")
    data.brickCard = brickCard
    rockCard = PhotoImage(file="photos/images/catanPieces/rockCard.gif")
    data.rockCard = rockCard
    wheatCard = PhotoImage(file="photos/images/catanPieces/wheatCard.gif")
    data.wheatCard = wheatCard
    vpCard = PhotoImage(file="photos/images/catanPieces/vp.gif")
    data.vpCard = vpCard
    roadBuildingCard = PhotoImage(file="photos/images/catanPieces/\
roadbuilding.gif")
    data.roadBuildingCard = roadBuildingCard
    knightCard = PhotoImage(file="photos/images/catanPieces/knight.gif")
    data.knightCard = knightCard

    data.allCards = [data.fieldCard, data.forestCard, data.brickCard,
                     data.rockCard, data.wheatCard, data.vpCard, \
                     data.roadBuildingCard,
                     data.knightCard]

###############################################################################
    # die
    die1 = PhotoImage(file="photos/images/die/1.gif")
    data.die1 = die1
    die2 = PhotoImage(file="photos/images/die/2.gif")
    data.die2 = die2
    die3 = PhotoImage(file="photos/images/die/3.gif")
    data.die3 = die3
    die4 = PhotoImage(file="photos/images/die/4.gif")
    data.die4 = die4
    die5 = PhotoImage(file="photos/images/die/5.gif")
    data.die5 = die5
    die6 = PhotoImage(file="photos/images/die/6.gif")
    data.die6 = die6

    data.allDie = [data.die1, data.die2, data.die3, data.die4, \
    data.die5, data.die6]

###############################################################################
    # number cards
    tile12 = PhotoImage(file="photos/images/catanPieces/12.gif")
    data.tile12 = tile12
    tile2 = PhotoImage(file="photos/images/catanPieces/2.gif")
    data.tile2 = tile2
    tile3 = PhotoImage(file="photos/images/catanPieces/3.gif")
    data.tile3 = tile3
    tile4 = PhotoImage(file="photos/images/catanPieces/4.gif")
    data.tile4 = tile4
    tile5 = PhotoImage(file="photos/images/catanPieces/5.gif")
    data.tile5 = tile5
    tile6 = PhotoImage(file="photos/images/catanPieces/6.gif")
    data.tile6 = tile6
    tile8 = PhotoImage(file="photos/images/catanPieces/8.gif")
    data.tile8 = tile8
    tile9 = PhotoImage(file="photos/images/catanPieces/9.gif")
    data.tile9 = tile9
    tile10 = PhotoImage(file="photos/images/catanPieces/10.gif")
    data.tile10 = tile10
    tile11 = PhotoImage(file="photos/images/catanPieces/11.gif")
    data.tile11 = tile11


###############################################################################
    # text
    clickToIncrease = PhotoImage(file="photos/images/text/c_increase.gif")
    data.clickToIncrease = clickToIncrease
    cToContinue = PhotoImage(file="photos/images/text/c_continue.gif")
    data.cToContinue = cToContinue
    forText = PhotoImage(file="photos/images/text/for_image.gif")
    data.forText = forText
    myHandText = PhotoImage(file="photos/images/text/my_hand.gif")
    data.myHandText = myHandText
    noCollect = PhotoImage(file="photos/images/text/no_collect.gif")
    data.noCollect = noCollect
    pleaseWait = PhotoImage(file="photos/images/text/please_wait.gif")
    data.pleaseWait = pleaseWait
    tradeText = PhotoImage(file="photos/images/text/trade_image.gif")
    data.tradeText = tradeText


###############################################################################
    data.allTiles = [data.tile2, data.tile3, data.tile4, data.tile5, \
    data.tile6, 0,
                     data.tile8, data.tile9, data.tile10, data.tile11,data.tile12]



    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

serverMsg = Queue(100)
threading.Thread(target = handleServerMsg, args = (server, serverMsg)).start()
ez()
run(750, 750, serverMsg, server)
