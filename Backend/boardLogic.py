###############################################################################
# board logic, sets up how to game board is represented in memory and
# handles the updating of the baord
###############################################################################

class GameBoard(object):
    # first what kind of house
    # second distance to draw
    # third index
    boardVerticies = [
[0,(6,4),1],[0,(8,4),2],[0,(10,4),3],
[0,(5,5),4],[0,(7,5),5],[0,(9,5),6],[0,(11,5),7],
[0,(5,7),8],[0,(7,7),9],[0,(9,7),10],[0,(11,7),11],
[0,(4,8),12],[0,(6,8),13],[0,(8,8),14],[0,(10,8),15],[0,(12,8),16],
[0,(4,10),17],[0,(6,10),18],[0,(8,10),19],[0,(10,10),20],[0,(12,10),21],
[0,(3,11),22],[0,(5,11),23],[0,(7,11),24],[0,(9,11),25],[0,(11,11),26],
[0,(13,11),27],[0,(3,13),28],[0,(5,13),29],[0,(7,13),30],[0,(9,13),31],
[0,(11,13),32],[0,(13,13),33],[0,(4,14),34],[0,(6,14),35],[0,(8,14),36],
[0,(10,14),37],[0,(12,14),38],[0,(4,16),39],[0,(6,16),40],[0,(8,16),41],
[0,(10,16),42],[0,(12,16),43],[0,(5,17),44],[0,(7,17),45],[0,(9,17),46],
[0,(11,17),47],[0,(5,19),48],[0,(7,19),49],[0,(9,19),50],[0,(11,19),51],
[0,(6,20),52],[0,(8,20),53],[0,(10,20),54]]

    # first index
    # second position
    # third value

    boardSides =      [[1,(5,5,6,4),0],[2,(6,4,7,5),0],
                       [3,(7,5,8,4),0],[4,(8,4,9,5),0],
                       [5,(9,5,10,4),0],[6,(10,4,11,5),0],
                       [7,(5,5,5,7),0],[8,(7,5,7,7),0],
                       [9,(9,5,9,7),0],[10,(11,5,11,7),0],
                       [11,(4,8,5,7),0],[12,(5,7,6,8),0],
                       [13,(6,8,7,7),0],[14,(7,7,8,8),0],
                       [15,(8,8,9,7),0],[16,(9,7,10,8),0],
                       [17,(10,8,11,7),0],[18,(11,7,12,8),0],
                       [19,(4,8,4,10),0],[20,(6,8,6,10),0],
                       [21,(8,8,8,10),0],[22,(10,8,10,10),0],
                       [23,(12,8,12,10),0],[24,(3,11,4,10),0],
                       [25,(4,10,5,11),0],[26,(5,11,6,10),0],
                       [27,(6,10,7,11),0],[28,(7,11,8,10),0],
                       [29,(8,10,9,11),0],[30,(9,11,10,10),0],
                       [31,(10,10,11,11),0],[32,(11,11,12,10),0],
                       [33,(12,10,13,11),0],[34,(3,11,3,13),0],
                       [35,(5,11,5,13),0],[36,(7,11,7,13),0],
                       [37,(9,11,9,13),0],[38,(11,11,11,13),0],
                       [39,(13,11,13,13),0],[40,(3,13,4,14),0],
                       [41,(4,14,5,13),0],[42,(5,13,6,14),0],
                       [43,(6,14,7,13),0],[44,(7,13,8,14),0],
                       [45,(8,14,9,13),0],[46,(9,13,10,14),0],
                       [47,(10,14,11,13),0],[48,(11,13,12,14),0],
                       [49,(12,14,13,13),0],[50,(4,14,4,16),0],
                       [51,(6,14,6,16),0],[52,(8,14,8,16),0],
                       [53,(10,14,10,16),0],[54,(12,14,12,16),0],
                       [55,(4,16,5,17),0],[56,(5,17,6,16),0],
                       [57,(6,16,7,17),0],[58,(7,17,8,16),0],
                       [59,(8,16,9,17),0],[60,(9,17,10,16),0],
                       [61,(10,16,11,17),0],[62,(11,17,12,16),0],
                       [63,(5,17,5,19),0],[64,(7,17,7,19),0],
                       [65,(9,17,9,19),0],[66,(11,17,11,19),0],
                       [67,(5,19,6,20),0],[68,(6,20,7,19),0],
                       [69,(7,19,8,20),0],[70,(8,20,9,19),0],
                       [71,(9,19,10,20),0],[72,(10,20,11,19),0]]

    # basic is legal only checking if something is there
    # will add rules like one or two away later
    @staticmethod
    def isLegalSide(n):
        # check if 0 where we want to put thing
        return (GameBoard.boardSides[n][2] == 0)

    # add roads which go on the sides
    @staticmethod
    def updateSide(side, color):
          GameBoard.boardSides[side][2] = color

    # add settlements on the verticies
    @staticmethod
    def updateVerticie(verticie, color):
        GameBoard.boardVerticies[verticie][0] = color



###############################################################################
# initializes the hexes that take their sides and verst
class Hex(GameBoard):
    def __init__(self, s1, s2, s3, s4, s5, s6,
                v1, v2, v3, v4, v5, v6, n, attr="white", raider=False,
                roll=0):
        self.s1 = GameBoard.boardSides[s1-1]
        self.s2 = GameBoard.boardSides[s2-1]
        self.s3 = GameBoard.boardSides[s3-1]
        self.s4 = GameBoard.boardSides[s4-1]
        self.s5 = GameBoard.boardSides[s5-1]
        self.s6 = GameBoard.boardSides[s6-1]
        self.v1 = GameBoard.boardVerticies[v1-1]
        self.v2 = GameBoard.boardVerticies[v2-1]
        self.v3 = GameBoard.boardVerticies[v3-1]
        self.v4 = GameBoard.boardVerticies[v4-1]
        self.v5 = GameBoard.boardVerticies[v5-1]
        self.v6 = GameBoard.boardVerticies[v6-1]
        self.n = n
        self.attr = attr
        self.roll = roll
        self.raider = raider

# represent for eval
    def __repr__(self):
        return "HexBoard.hex" + str(self.n)

    def number(self):
        return self.n



###############################################################################
# gives each hex it's game attributes
class  HexBoard(Hex):
    hex1 = Hex(7,1,2,8,13,12,4,1,5,9,13,8,1)
    hex2 = Hex(8,3,4,9,15,14,5,2,6,10,14,9,2)
    hex3 = Hex(9,5,6,10,17,16,6,3,7,11,15,10,3)
    hex4 = Hex(19,11,12,20,26,25,12,8,13,18,23,17,4)
    hex5 = Hex(20,13,14,21,28,27,13,9,14,19,24,18,5)
    hex6 = Hex(21,15,16,22,30,29,14,10,15,20,25,19,6)
    hex7 = Hex(22,17,18,23,32,31,15,11,16,21,26,20,7)
    hex8 = Hex(34,24,25,35,41,40,22,17,23,29,34,28,8)
    hex9 = Hex(35,26,27,36,43,42,23,18,24,30,35,29,9)
    hex10 = Hex(36,28,29,37,45,44,24,19,25,31,36,30,10)
    hex11 = Hex(37,30,31,38,47,46,25,20,26,32,37,31,11)
    hex12 = Hex(38,32,33,29,49,48,26,21,27,33,38,32,12)
    hex13 = Hex(50,41,42,51,56,55,34,29,35,40,44,39,13)
    hex14 = Hex(51,43,44,52,58,57,35,30,36,41,45,40,14)
    hex15 = Hex(52,45,46,53,60,59,36,31,37,42,46,41,15)
    hex16 = Hex(53,47,48,54,62,61,37,32,38,43,47,42,16)
    hex17 = Hex(63,56,57,64,68,67,44,40,45,49,52,48,17)
    hex18 = Hex(64,58,59,65,70,69,45,41,46,50,53,49,18)
    hex19 = Hex(65,60,61,66,72,71,46,42,47,51,54,50,19)





    @staticmethod
    def updateHexes():
        HexBoard.hex1 = Hex(7,1,2,8,13,12,4,1,5,9,13,8,1)
        HexBoard.hex2 = Hex(8,3,4,9,15,14,5,2,6,10,14,9,2)
        HexBoard.hex3 = Hex(9,5,6,10,17,16,6,3,7,11,15,10,3)
        HexBoard.hex4 = Hex(19,11,12,20,26,25,12,8,13,18,23,17,4)
        HexBoard.hex5 = Hex(20,13,14,21,28,27,13,9,14,19,24,18,5)
        HexBoard.hex6 = Hex(21,15,16,22,30,29,14,10,15,20,25,19,6)
        HexBoard.hex7 = Hex(22,17,18,23,32,31,15,11,16,21,26,20,7)
        HexBoard.hex8 = Hex(34,24,25,35,41,40,22,17,23,29,34,28,8)
        HexBoard.hex9 = Hex(35,26,27,36,43,42,23,18,24,30,35,29,9)
        HexBoard.hex10 = Hex(36,28,29,37,45,44,24,19,25,31,36,30,10)
        HexBoard.hex11 = Hex(37,30,31,38,47,46,25,20,26,32,37,31,11)
        HexBoard.hex12 = Hex(38,32,33,29,49,48,26,21,27,33,38,32,12)
        HexBoard.hex13 = Hex(50,41,42,51,56,55,34,29,35,40,44,39,13)
        HexBoard.hex14 = Hex(51,43,44,52,58,57,35,30,36,41,45,40,14)
        HexBoard.hex15 = Hex(52,45,46,53,60,59,36,31,37,42,46,41,15)
        HexBoard.hex16 = Hex(53,47,48,54,62,61,37,32,38,43,47,42,16)
        HexBoard.hex17 = Hex(63,56,57,64,68,67,44,40,45,49,52,48,17)
        HexBoard.hex18 = Hex(64,58,59,65,70,69,45,41,46,50,53,49,18)
        HexBoard.hex19 = Hex(65,60,61,66,72,71,46,42,47,51,54,50,19)


###############################################################################
    @staticmethod
    def returnHexSide(hexNum, side):
        HexBoard.updateHexes()

    @staticmethod
    def changeType(hexagon, attribute):
        hexagon.attr = attribute
        hexagon = Hex(hexagon.s1[0],hexagon.s2[0],hexagon.s3[0],hexagon.s4[0],
                                                  hexagon.s5[0],hexagon.s6[0],
                      hexagon.v1[2],hexagon.v2[2],hexagon.v3[2],hexagon.v4[2],
                                                  hexagon.v5[2],hexagon.v6[2],
                      hexagon.number(), attr = attribute)

    @staticmethod
    def changeRoll(hexagon, newRoll):
        hexagon.roll = newRoll
        hexagon = Hex(hexagon.s1[0],hexagon.s2[0],hexagon.s3[0],hexagon.s4[0],
                                                  hexagon.s5[0],hexagon.s6[0],
                      hexagon.v1[2],hexagon.v2[2],hexagon.v3[2],hexagon.v4[2],
                                                  hexagon.v5[2],hexagon.v6[2],
                      hexagon.number(), roll = newRoll)

    @staticmethod
    def moveRaider(newHex, oldHex):
        if oldHex == newHex:
          return
        oldHex.raider = False
        newHex.raider = True
        oldHex = Hex(oldHex.s1[0],oldHex.s2[0],oldHex.s3[0],oldHex.s4[0],
                      oldHex.s5[0],oldHex.s6[0],
                      oldHex.v1[2],oldHex.v2[2],oldHex.v3[2],oldHex.v4[2],
                      oldHex.v5[2],oldHex.v6[2],
                      oldHex.number(), raider=False)
        newHex = Hex(newHex.s1[0],newHex.s2[0],newHex.s3[0],newHex.s4[0],
          newHex.s5[0],newHex.s6[0],
                      newHex.v1[2],newHex.v2[2],newHex.v3[2],newHex.v4[2],
                      newHex.v5[2],newHex.v6[2],
                      newHex.number(), raider=True)



hexes                 = [ HexBoard.hex1, HexBoard.hex2,
                        HexBoard.hex3, HexBoard.hex4,
                        HexBoard.hex5, HexBoard.hex6,
                        HexBoard.hex7, HexBoard.hex8,
                        HexBoard.hex9, HexBoard.hex10,
                        HexBoard.hex11, HexBoard.hex12,
                        HexBoard.hex13, HexBoard.hex14,
                        HexBoard.hex15, HexBoard.hex16,
                        HexBoard.hex17, HexBoard.hex18,
                        HexBoard.hex19]

def check():
    for i in range(len(hexes)):
        print("hex " + str(i) + " attr: " + hexes[i].attr)
        print("hex " + str(i) + " roll: " + str(hexes[i].roll))


