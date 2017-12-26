###############################################################################
# the ai file, the ai representation of the board and decidion making
###############################################################################

import socket
import threading
import math
import easyGameInit
import random
import itertools
from queue import Queue
from boardLogic import *
from legalMove import *
from chance import *

###############################################################################
# sockets
# framework based on example by Rohan Varma and Kyle Chin
###############################################################################


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

serverMsg = Queue(100)
threading.Thread(target=handleServerMsg, args=(server, serverMsg)).start()



###############################################################################
def executeCommand(data):
	checkGameOver(data)
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

		elif command == "buildRoad":
			road = int(msg[2])
			color = int(msg[3])
			state.buildRoads.append((road + 1, color))
			GameBoard.updateSide(road, color)
			updateCurrentGraph()

		elif command == "buildHouse":
			house = int(msg[2])
			color = int(msg[3])
			state.buildHouses.append((house + 1, color))
			GameBoard.updateVerticie(house, color)
			updateCurrentGraph()

		elif command == "rolled":
			roll = int(msg[2])
			resources = collectResources(data, roll, state.myColor)
			updateHand(resources)
			if roll == 7:
				# find my hexes
				state.listHand = getListHand(state.myHand)
				handLength = len(state.listHand)
				lengthCheck = len(state.listHand)
				if handLength > 7:
					while handLength > lengthCheck//2:
						for key in state.myHand:
							if state.myHand[key] > 0:
								state.myHand[key] -= 1
								handLength -= 1
								break

###############################################################################
		elif command == "endTurn":
			lastPlayer = msg[2]
			nextPlayer = (state.orderOfPlay.index(lastPlayer) + 1) \
            % len(state.orderOfPlay)
			state.currentPlayer = nextPlayer

		elif command == "trade":
			sorryMessage = "cantTrade sorry\n"
			data.server.send(sorryMessage.encode())

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
			else:
				tradeStateSwap()

		elif command == "Raider":
			nextPos = msg[3]
			moveRaider(data, eval(nextPos), \
                data.hexObjects[findRaider(data)])

###############################################################################
		elif command == "steal":
			newPlayer = msg[2]
			if newPlayer == state.myID:
				state.listHand = getListHand(state.myHand)
				if len(state.listHand) != 0:
					resource = ""
					for key in state.myHand:
						if state.myHand[key] < 0:
							resource = key
							removeDict = {resource:-1}
							updateHand(removeDict)
							message = "add " + player + " " + resource + "\n"
							data.server.send(message.encode())
							break

###############################################################################
		elif command == "add":
			newPlayer = msg[2]
			resource = msg[3]
			if newPlayer == state.myID:
				resourceAdd = {resource:1}
				updateHand(resourceAdd)

		elif command == "ai":
			numPlayers = state.myID[-1]
			state.myColor = int(numPlayers)
			if state.myColor == 2:
				state.players.append("Player1")
				easyTwoPlayer()
			elif state.myColor == 3:
				state.players.append("Player1")
				state.players.append("Player2")
				easyThreePlayer()
			elif state.myColor == 4:
				state.players.append("Player1")
				state.players.append("Player2")
				state.players.append("Player3")
				easyFourPlayer()

			initializeBoard()
			updateCurrentGraph()

			state.targetResource = chooseMonopoly(state.myColor)
			state.currentStrategy += 1
			addMessage = "addPlayer " + state.myID + " " + "ConnorJr" + "\n"
			data.server.send(addMessage.encode())

			state.orderOfPlay = sorted(state.players)



		serverMsg.task_done()


###############################################################################
# gameplay related
###############################################################################


# globals
rolledSeven = False
moreThanSeven = False



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

###############################################################################
def getNode(x, y):
    for vertex in GameBoard.boardVerticies:
        if x == vertex[1][0] and y == vertex[1][1]:
            return vertex[2]


###############################################################################
def checkGameOver(data):
    updateScore(data)
    for key in state.scores:
        if state.scores[key] >= state.winCondition:
            state.gameOver = True
            message = "gameOver " + str(state.scores[state.myID]) + "\n"
            data.server.send(message.encode())
            if state.scores[state.myID] >= state.winCondition:
                state.winner = state.myID

###############################################################################
def longestRoad(color):
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

###############################################################################
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

###############################################################################
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

    if state.myID != "":
    	state.scores[state.myID] += state.myHand["Vp"]

    playerLongestRoad()

###############################################################################
def getListHand(myHand):
	handList = []
	for key in myHand:
		for i in range(myHand[key]):
			handList.append(key)
	return handList

###############################################################################
def updateHand(d):
	for key in d:
		state.myHand[key] += d[key]


###############################################################################
def collectResources(data, roll, myColor):
    collect = {}
    for i in range(len(data.hexObjects)):
        if roll == data.hexObjects[i].roll:
            resource = state.colorToResource[data.hexObjects[i].attr]
            if myColor == data.hexObjects[i].v1[0]:
                collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v2[0]:
                collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v3[0]:
                collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v4[0]:
                collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v5[0]:
                collect[resource] = collect.get(resource, 0) + 1
            if myColor == data.hexObjects[i].v6[0]:
                collect[resource] = collect.get(resource, 0) + 1
    return collect

###############################################################################
def legalTrade(myResource, myNumber):
    return state.myHand[myResource] >= int(myNumber)


###############################################################################
def tradeStateSwap(theirNumber=0, theirResource="", myNumber=0, myResource="", them=""):
    state.trading = not state.trading
    state.theirNumber = theirNumber
    state.theirResource = theirResource
    state.myNumber = myNumber
    state.myResource = myResource
    state.them = them

###############################################################################
def moveRaider(data, newHex, oldHex=HexBoard.hex10):
    HexBoard.moveRaider(newHex, oldHex)
    init(data)
    return playersOnHex(data, newHex)

###############################################################################
def findRaider(data):
    for i in range(len(data.hexObjects)):
        if data.hexObjects[i].raider:
            return i
    return 9

###############################################################################
def orderPlayers():
	state.orderOfPlay = sorted(state.players)

###############################################################################
def playersOnHex(data, newHex):
    players = []
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

###############################################################################
# state set up
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
        "Wheat":20,
        "Rock":20,
        "Brick":20,
        "Sheep":20,
        "Lumber":20,
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

state.hexObjects = [ HexBoard.hex1, HexBoard.hex2,
                        HexBoard.hex3, HexBoard.hex4,
                        HexBoard.hex5, HexBoard.hex6,
                        HexBoard.hex7, HexBoard.hex8,
                        HexBoard.hex9, HexBoard.hex10,
                        HexBoard.hex11, HexBoard.hex12,
                        HexBoard.hex13, HexBoard.hex14,
                        HexBoard.hex15, HexBoard.hex16,
                        HexBoard.hex17, HexBoard.hex18,
                        HexBoard.hex19]

state.startPositions = {}
state.winner = ""
state.winCondition = 10

state.currentLongestRoad = ""
state.currentLongestRoadLength = 0


###############################################################################
# data set up
###############################################################################
class Struct(object): pass
data = Struct()
data.server = server
data.serverMsg = serverMsg

def init(data):
	data.hexObjects =     [ HexBoard.hex1, HexBoard.hex2,
	                        HexBoard.hex3, HexBoard.hex4,
	                        HexBoard.hex5, HexBoard.hex6,
	                        HexBoard.hex7, HexBoard.hex8,
	                        HexBoard.hex9, HexBoard.hex10,
	                        HexBoard.hex11, HexBoard.hex12,
	                        HexBoard.hex13, HexBoard.hex14,
	                        HexBoard.hex15, HexBoard.hex16,
	                        HexBoard.hex17, HexBoard.hex18,
	                        HexBoard.hex19]

init(data)




###############################################################################
# ai initialize
###############################################################################
state.gameStrategies = ["pregame", "early", "mid", "end"]
state.currentStrategy = 0
state.targetResource = ""




# initialize board
easyGameInit.ez()

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


def initializeBoard():
	for i in range(len(state.buildRoads)):
		index = state.buildRoads[i][0]
		color = state.buildRoads[i][1]
		GameBoard.updateSide(index, color)
	for i in range(len(state.buildHouses)):
		index = state.buildHouses[i][0]
		color = state.buildHouses[i][1]
		GameBoard.updateVerticie(index, color)

easyTwoPlayer()
initializeBoard()


###############################################################################
# graph representation of board node -> list of nodes, node -> checked
#
# boardGraph, graphCheck - main board without any account of players
# current -- board with deleted vertecies based on player position
###############################################################################


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
graphCheck = {
	1 : False,
	2 : False,
	3 : False,
	4 : False,
	5 : False,
	6 : False,
	7 : False,
	8 : False,
	9 : False,
	10 : False,
	11 : False,
	12 : False,
	13 : False,
	14 : False,
	15 : False,
	16 : False,
	17 : False,
	18 : False,
	19 : False,
	20 : False,
	21 : False,
	22 : False,
	23 : False,
	24 : False,
	25 : False,
	26 : False,
	27 : False,
	28 : False,
	29 : False,
	30 : False,
	31 : False,
	32 : False,
	33 : False,
	34 : False,
	35 : False,
	36 : False,
	37 : False,
	38 : False,
	39 : False,
	40 : False,
	41 : False,
	42 : False,
	43 : False,
	44 : False,
	45 : False,
	46 : False,
	47 : False,
	48 : False,
	49 : False,
	50 : False,
	51 : False,
	52 : False,
	53 : False,
	54 : False,
}

currentGraph = {
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

currentGraphCheck = {
	1 : False,
	2 : False,
	3 : False,
	4 : False,
	5 : False,
	6 : False,
	7 : False,
	8 : False,
	9 : False,
	10 : False,
	11 : False,
	12 : False,
	13 : False,
	14 : False,
	15 : False,
	16 : False,
	17 : False,
	18 : False,
	19 : False,
	20 : False,
	21 : False,
	22 : False,
	23 : False,
	24 : False,
	25 : False,
	26 : False,
	27 : False,
	28 : False,
	29 : False,
	30 : False,
	31 : False,
	32 : False,
	33 : False,
	34 : False,
	35 : False,
	36 : False,
	37 : False,
	38 : False,
	39 : False,
	40 : False,
	41 : False,
	42 : False,
	43 : False,
	44 : False,
	45 : False,
	46 : False,
	47 : False,
	48 : False,
	49 : False,
	50 : False,
	51 : False,
	52 : False,
	53 : False,
	54 : False,
}


###############################################################################
# Shortest Path Implementation
###############################################################################

def shortestPath(initial, target, graph, check):
	# try to find a length and path, if not return it's impossible
	# node to parent
	shortestPath = {}

	graphCopy = graph.copy()
	checkCopy = check.copy()

	# initialize shorest distance, everyting at inf other than start
	shortestDistance = {}
	for node in checkCopy:
		shortestDistance[node] = math.inf
	shortestDistance[initial] = 0

	# create queue of nodes to check
	checkNodes = Queue(54)

	# put start node into queue and initialize shortest path with this node
	checkNodes.put(initial)
	shortestPath[initial] = None

	# update and push nodes until all have been checked
	while not checkNodes.empty():
		currentNode = checkNodes.get()
		for node in graphCopy[currentNode]:
			# keep track of parent of node
			shortestDistance[node] = min(shortestDistance[currentNode]+1, \
                shortestDistance[node])
			if not checkCopy[node]:
				shortestPath[node] = currentNode
				checkNodes.put(node)
		checkCopy[currentNode] = True
	return (shortestDistance[target], shortestPath)



###############################################################################
def shortestPathSteps(initial, target, graph, check):
	path = shortestPath(initial, target, graph, check)[1]
	start = target
	vertecies = []
	while start in path and path[start] != None:
		vertecies.append((path[start], start))
		start = path[start]
	if not start in path:
		return None
	return vertecies[::-1]


###############################################################################
def updateGraph(vertex, graph, check):
	global currentGraph
	global currentGraphCheck

	for key in currentGraph:
		for v in currentGraph[key]:
			if v == vertex:
				currentGraph[key].remove(v)

	currentGraph.pop(vertex, None)
	currentGraphCheck.pop(vertex, None)

###############################################################################
def findDistances(start, targetType, graph, check):
	distances = []
	hexesWithAttr = []
	possibleEnd = []

	for i in range(len(state.hexObjects)):
		if state.hexObjects[i].attr == targetType:
			hexesWithAttr.append(i)

	for hexx in hexesWithAttr:
		possibleEnd.append(state.hexObjects[hexx].v1[2])
		possibleEnd.append(state.hexObjects[hexx].v2[2])
		possibleEnd.append(state.hexObjects[hexx].v3[2])
		possibleEnd.append(state.hexObjects[hexx].v4[2])
		possibleEnd.append(state.hexObjects[hexx].v5[2])
		possibleEnd.append(state.hexObjects[hexx].v6[2])

	for end in possibleEnd:
		if end in currentGraphCheck and start in currentGraphCheck:
			if shortestPathSteps(start, end, currentGraph, currentGraphCheck)\
             != None:
				distances.append(shortestPathSteps(start, end, currentGraph,\
                 currentGraphCheck))
			else:
				pass
	return distances

###############################################################################
def findStartPositions(myColor, boardVerticies):
	state.startPositions = {}
	startPositions = []
	# house start
	for i in range(len(boardVerticies)):
		if boardVerticies[i][0] == state.myColor:
			startPositions.append(boardVerticies[i][2])
	# road start
	for i in range(len(GameBoard.boardSides)):
		if GameBoard.boardSides[i][2] == state.myColor:
			check1 = (GameBoard.boardSides[i][1][0], \
                GameBoard.boardSides[i][1][1])
			check2 = (GameBoard.boardSides[i][1][2], \
                GameBoard.boardSides[i][1][3])
			for j in range(len(GameBoard.boardVerticies)):
				if check1 in GameBoard.boardVerticies[j]:
					startPositions.append(GameBoard.boardVerticies[j][2])
				if check2 in GameBoard.boardVerticies[j]:
					startPositions.append(GameBoard.boardVerticies[j][2])

	state.startPositions = set(startPositions)

	return list(set(startPositions))


###############################################################################
def shortestDistance(myColor, targetType):
	startPositions = findStartPositions(state.myColor,\
     GameBoard.boardVerticies)
	distances = []
	allDistances = []
	for start in startPositions:
		distances.append(findDistances(start, targetType, \
            currentGraph, currentGraphCheck))

	for d in distances:
		hexDistances = []
		for distance in d:
			allDistances.append(len(distance))
	return sum(allDistances)/len(allDistances)

###############################################################################
def resourcePriority():
	brick = []
	lumber = []
	brickProb = 0
	lumberProb = 0
	for i in range(len(state.hexObjects)):
		if state.hexObjects[i].attr == "red":
			brick.append(state.hexObjects[i].roll)
		if state.hexObjects[i].attr == "brown":
			lumber.append(state.hexObjects[i].roll)
	for i in range(len(brick)):
		brickProb += abs(7-brick[i])
	for i in range(len(lumber)):
		lumberProb += abs(7-lumber[i])

	return (brickProb/len(brick), lumberProb/len(lumber))


###############################################################################
def chooseMonopoly(myColor):
	lumberDistance = shortestDistance(myColor, "brown")
	brickDistance = shortestDistance(myColor, "red")
	brickProb, lumberProb = resourcePriority()
	lumberIndex = lumberDistance * lumberProb
	brickIndex = brickDistance * brickProb

	if lumberIndex > brickIndex:
		return "brown"
	else:
		return "red"

###############################################################################
def updateGameBoard():
	# update houses
	for house in state.buildHouses:
		GameBoard.updateVerticie(house[0]-1, house[1])
	# update roads
	for road in state.buildRoads:
		GameBoard.updateSide(road[0]-1, road[1])

###############################################################################
def updateCurrentGraph():
	# add where we update board from build roads and build houses
	colorCount = {}
	blockedPositions = []


	# initialize count of colors
	for i in range(len(GameBoard.boardVerticies)):
		colorCount[i+1] = 0

	# add count for touching verticies
	for i in range(len(GameBoard.boardVerticies)):
		vertex = GameBoard.boardVerticies[i]
		color = vertex[0]
		position = vertex[2]
		if color != 0 and (position,state.myColor) not in state.startPositions\
        and state.myColor != color:
			colorCount[i+1] += 1

	# add count for roads touching verticies
	for i in range(len(GameBoard.boardSides)):
		side = GameBoard.boardSides[i]
		color = side[2]
		position = side[0]
		if color != 0 and (position,state.myColor) not in state.startPositions:
			check1 = (side[1][0], side[1][1])
			check2 = (side[1][2], side[1][3])
			for j in range(len(GameBoard.boardVerticies)):
				vertex = GameBoard.boardVerticies[j]
				if check1 in vertex:
					colorCount[vertex[2]] += 1
				if check2 in vertex:
					colorCount[vertex[2]] += 1

	# if more than two of a color are touching a verticie, it's blocked
	for key in colorCount:
		if colorCount[key] >= 2:
			blockedPositions.append(key)

	# update graph with information
	for vertex in blockedPositions:
		updateGraph(vertex, currentGraph, currentGraphCheck)

###############################################################################
# strategy conditions
###############################################################################

def roadCount():
	return len(set(state.buildRoads))

def settlementCount():
	return len(set(state.buildHouses))

def cityCount():
	return len(set(state.buildCities))

def vpCount():
	return state.myScore



###############################################################################
# try build
###############################################################################

def trySettlements(resource):
	for i in range(len(GameBoard.boardVerticies)):
		vertex = GameBoard.boardVerticies[i]
		vColor = vertex[0]
		position = vertex[2]
		if vColor == 0:
			if gameLegalHouse(position-1, state.myColor):
				canBuy = True
				for key in state.houseCost:
					if state.myHand[key] - state.houseCost[key] < 0:
						canBuy = False
						continue
				if canBuy:
					for key in state.houseCost:
						state.myHand[key] -= state.houseCost[key]
					state.buildHouses.append((position, state.myColor))
					message = "buildHouse " + str(position-1) + " " \
                    + str(state.myColor) + "\n"
					data.server.send(message.encode())
					GameBoard.updateVerticie(position-1, state.myColor)
					updateCurrentGraph()

###############################################################################
def tryCities(resource):
	for i in range(len(state.buildHouses)):
		if state.buildHouses[i][1] == state.myColor:
			canBuy = True
			if state.buildHouses[i] in state.buildCities:
				return False
			for key in state.cityCost:
				if state.myHand[key] - state.cityCost[key] < 0:
					canBuy = False
					continue
			if canBuy:
				for key in state.cityCost:
					state.myHand[key] -= state.cityCost[key]
				message = "buildCity " + str(state.buildHouses[i][0]) + \
                " " + str(state.buildHouses[i][1]) + "\n"
				data.server.send(message.encode())
				state.buildCities.append(state.buildHouses[i])


###############################################################################
def tryRoads(resource):
    try:
    	# sort paths by length
    	startPositions = findStartPositions(state.myColor, \
            GameBoard.boardVerticies)
    	paths = []

    	for start in startPositions:
    		paths.append(findDistances(start, resource, \
                currentGraph, currentGraphCheck))
    	pathLengths = []
    	for path in paths:
    		for chain in path:
    			pathLengths.append((len(chain),chain))
    	pathLengths.sort()

    	# filter paths that end in a buildable settlement
    	pathFilter = []
    	for path in pathLengths:
    		if path[0] == 0:
    			continue
    		if startLegalHouse(path[1][-1][-1]-1, state.myColor):
    			pathFilter.append(path[1])


    	# associate road to path
    	roadToBuild = pathFilter[0][0]
    	vertex1 = list(GameBoard.boardVerticies[roadToBuild[0]-1][1])
    	vertex2 = list(GameBoard.boardVerticies[roadToBuild[1]-1][1])
    	check1 = tuple(vertex1 + vertex2)
    	check2 = tuple(vertex2 + vertex1)
    	for i in range(len(GameBoard.boardSides)):
    		side = GameBoard.boardSides[i]
    		check = side[1]
    		if check1 == check or check2 == check:
    			for key in state.roadCost:
    				if state.myHand[key] - state.roadCost[key] < 0:
    					return False
    			for key in state.roadCost:
    				state.myHand[key] -= state.roadCost[key]
    			state.buildRoads.append((side[0], state.myColor))
    			message = "buildRoad " + str(side[0]-1) + " " + \
                str(state.myColor) + "\n"
    			data.server.send(message.encode())
    			GameBoard.updateSide(side[0]-1, state.myColor)
    			updateCurrentGraph()
    except:
        return None



###############################################################################
def tryBuyDevCard():
	for key in state.developmentCardCost:
		if state.myHand[key] - state.developmentCardCost[key] < 0:
			return
	for key in state.developmentCardCost:
		state.myHand[key] -= state.developmentCardCost[key]
	index = random.randint(0,2)
	devCards = ["Knight", "Vp", "RoadBuilding"]
	myDevCard = devCards[index]
	updateDict = {myDevCard:1}
	updateHand(updateDict)
	if myDevCard == "Knight":
		state.totalKnights += 1

###############################################################################
def findHexes(color):
	hexes = []
	houses = []
	for i in range(len(GameBoard.boardVerticies)):
		vertex = GameBoard.boardVerticies[i]
		hColor = vertex[0]
		if color == hColor:
			houses.append(i+1)


	for i in range(len(data.hexObjects)):
		hexx = data.hexObjects[i]
		if hexx.v1[2] in houses:
			hexes.append(i+1)
		if hexx.v2[2] in houses:
			hexes.append(i+1)
		if hexx.v3[2] in houses:
			hexes.append(i+1)
		if hexx.v4[2] in houses:
			hexes.append(i+1)
		if hexx.v5[2] in houses:
			hexes.append(i+1)
		if hexx.v6[2] in houses:
			hexes.append(i+1)

	return set(hexes)

###############################################################################
# strategy
###############################################################################

def aiPlay():
	if state.gameStrategies[state.currentStrategy] == "early":
		trySettlements(state.targetResource)
		tryRoads(state.targetResource)
		tryCities(state.targetResource)
		state.listHand = getListHand(state.myHand)
		if len(state.listHand) > 7:
			tryBuyDevCard()
		if roadCount() >= 30 or settlementCount() >= 20:
			state.currentStrategy += 1

	elif state.gameStrategies[state.currentStrategy] == "mid":

		trySettlements(state.targetResource)
		tryCities(state.targetResource)
		tryRoads(state.targetResource)
		state.listHand = getListHand(state.myHand)
		if len(state.listHand) > 7:
			tryBuyDevCard()

		# change conditions
		if vpCount >= 8 or cityCost >= 12:
			state.currentStrategy += 1

	elif state.gameStrategies[state.currentStrategy] == "end":

		tryBuyDevCard(state.targetResource)
		tryCities(state.targetResource)
		trySettlements(state.targetResource)
		tryRoads(state.targetResource)


###############################################################################
# turn anatomy
###############################################################################
playing = True

while playing:


	executeCommand(data)


	# if not my turn only process other players
	if state.orderOfPlay[state.currentPlayer%len(state.orderOfPlay)] != state.myID:
		continue

	################################################################
	                     # start turn #
	################################################################

###############################################################################
	if rolledSeven:
		state.listHand = getListHand(state.myHand)
		handLength = len(state.listHand)
		lengthCheck = len(state.listHand)
		if handLength > 7:
			while handLength > lengthCheck//2:
				for key in state.myHand:
					if state.myHand[key] > 0:
						state.myHand[key] -= 1
						handLength -= 1
						break

		myHexes = findHexes(state.myColor)
		topScore = 0
		topPlayer = ""
		try:
			for key in state.scores:
				if state.scores[key] > topScore:
					topPlayer = key
			topPlayerColor = state.orderOfPlay.find(topPlayer) + 1
		except:
			topPlayerColor = (state.myColor + 1)%4 + 1
		topPlayerHexes = findHexes(topPlayerColor)
		moveTo = topPlayerHexes - myHexes
		if len(moveTo) != 0:
			moveList = list(moveTo)
			moveHex = moveList[0]
		else:
			moveHex = 9

		# send message of where to send
		moveRaider(data, data.hexObjects[moveHex], \
            data.hexObjects[findRaider(data)])
		message = "Raider " + str(data.hexObjects[moveHex]) + " " + \
        str(data.hexObjects[findRaider(data)]) + "\n"
		data.server.send(message.encode())

		# steal from player
		message = "steal " + topPlayer + "\n"
		data.server.send(message.encode())

		# break out of rolled seven
		rolledSeven = False
		state.currentStage += 1
		continue

###############################################################################
	elif state.stages[state.currentStage] == "start":
		# bypass login
		state.currentStage += 1
		continue


###############################################################################
	elif state.stages[state.currentStage] == "roll":
		roll1 = rollDie()
		roll2 = rollDie()
		state.roll = roll1 + roll2
		resources = collectResources(data, state.roll, state.myColor)
		updateHand(resources)
		# send message to players of what I rolled
		if state.roll == 7:
			rolledSeven = True
		state.currentStage += 1
		continue

###############################################################################
	elif state.stages[state.currentStage] == "trade":
		# find most and least elements
		most = []
		least = []
		for key in state.myHand:
			if key != "RoadBuilding" and key != "Knight" and key != "Vp":
				most.append((state.myHand[key], key))
				least.append((state.myHand[key], key))
		mostResource = sorted(most)[-1][1]
		leastResource = sorted(least)[0][1]

		if mostResource[0] == leastResource[0]:
			state.currentStage += 1
		else:
			message = "trade " + str(1) + " " + mostResource + \
            " " + str(1) + " " + leastResource + "\n"
			data.server.send(message.encode())

		state.currentStage += 1
		continue
		pass
###############################################################################
	elif state.stages[state.currentStage] == "buy":
		aiPlay()
		# decide which strategy to use
		# do everything you can in the strategy
		# end turn and wait
		state.currentStage = 1
		state.currentPlayer = (state.currentPlayer + 1) % len(state.orderOfPlay)
		message = "endTurn " + state.myID + "\n"
		data.server.send(message.encode())
		continue
	break























































