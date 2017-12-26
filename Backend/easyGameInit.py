###############################################################################
# sets up the board with the color and value of each hex and player 
# starting positioins
###############################################################################
from boardLogic import *
hexagons =            [ HexBoard.hex1, HexBoard.hex2,
                        HexBoard.hex3, HexBoard.hex4,
                        HexBoard.hex5, HexBoard.hex6,
                        HexBoard.hex7, HexBoard.hex8,
                        HexBoard.hex9, HexBoard.hex10,
                        HexBoard.hex11, HexBoard.hex12,
                        HexBoard.hex13, HexBoard.hex14,
                        HexBoard.hex15, HexBoard.hex16,
                        HexBoard.hex17, HexBoard.hex18,
                        HexBoard.hex19]

def ez():
    # types
    HexBoard.changeType(hexagons[0], "grey")
    HexBoard.changeType(hexagons[1], "brown")
    HexBoard.changeType(hexagons[2], "red")
    HexBoard.changeType(hexagons[3], "yellow")
    HexBoard.changeType(hexagons[4], "brown")
    HexBoard.changeType(hexagons[5], "grey")
    HexBoard.changeType(hexagons[6], "pink")
    HexBoard.changeType(hexagons[7], "grey")
    HexBoard.changeType(hexagons[8], "pink")
    HexBoard.changeType(hexagons[9], "black")
    HexBoard.changeType(hexagons[10], "yellow")
    HexBoard.changeType(hexagons[11], "yellow")
    HexBoard.changeType(hexagons[12], "yellow")
    HexBoard.changeType(hexagons[13], "brown")
    HexBoard.changeType(hexagons[14], "red")
    HexBoard.changeType(hexagons[15], "pink")
    HexBoard.changeType(hexagons[16], "pink")
    HexBoard.changeType(hexagons[17], "red")
    HexBoard.changeType(hexagons[18], "brown")

    # rolls
    HexBoard.changeRoll(hexagons[0], 8)
    HexBoard.changeRoll(hexagons[1], 4)
    HexBoard.changeRoll(hexagons[2], 6)
    HexBoard.changeRoll(hexagons[3], 11)
    HexBoard.changeRoll(hexagons[4], 2)
    HexBoard.changeRoll(hexagons[5], 12)
    HexBoard.changeRoll(hexagons[6], 10)
    HexBoard.changeRoll(hexagons[7], 5)
    HexBoard.changeRoll(hexagons[8], 9)
    HexBoard.changeRoll(hexagons[9], 2)
    HexBoard.changeRoll(hexagons[10], 11)
    HexBoard.changeRoll(hexagons[11], 9)
    HexBoard.changeRoll(hexagons[12], 3)
    HexBoard.changeRoll(hexagons[13], 8)
    HexBoard.changeRoll(hexagons[14], 3)
    HexBoard.changeRoll(hexagons[15], 6)
    HexBoard.changeRoll(hexagons[16], 10)
    HexBoard.changeRoll(hexagons[17], 4)
    HexBoard.changeRoll(hexagons[18], 5)

    # raider in middle
    HexBoard.moveRaider(HexBoard.hex10, HexBoard.hex1)





