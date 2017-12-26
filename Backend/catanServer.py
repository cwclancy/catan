# server code for people to play on

import socket, threading
from queue import Queue
# sockets server famework based on framework from Rohan Varma and Kyle Chin


HOST = ""
PORT = 50003
BACKLOG = 4

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(BACKLOG)
print("waiting for connection...")

def handleClient(client, serverChannel, cID, clientele):
    client.setblocking(1)
    msg = ""
    while True:
        try:
            msg += client.recv(10).decode("UTF-8")
            command = msg.split("\n")
            while (len(command) > 1):
                readyMsg = command[0]
                msg = "\n".join(command[1:])
                serverChannel.put(str(cID) + " " + readyMsg)
                command = msg.split("\n")
        except:
            clientele.pop(cID)
            return

def serverThread(clientele, serverChannel):
    while True:
        msg = serverChannel.get(True, None)
        print("msg recv: ", msg)
        msgList =  msg.split(" ")
        senderID = msgList[0]
        instruction = msgList[1]
        details = " ".join(msgList[2:])
        if details != "":
            for cID in clientele:
                if cID != senderID:
                    sendMsg = senderID + " " + instruction + " " + details + "\n"
                    clientele[cID].send(sendMsg.encode())
                    print("> send to %s:" % cID, sendMsg[:-1])
                    print("senderID: " + senderID,
                          "instrunciton: " + instruction,
                          "details: " + details)
        print()
        serverChannel.task_done()



clientele = dict()
playerNum = 0

# instructions to be executed
serverChannel = Queue(100)
threading.Thread(target = serverThread, args = (clientele, serverChannel)).start()

names = ["Player1", "Player2", "Player3", "Player4"]

while True:
    client, address = server.accept()

    #myID cleint key in client dictionary
    myID = names[playerNum]
    print(myID, playerNum)
    for cID in clientele:
        print(repr(cID), repr(playerNum))
        clientele[cID].send(("newPlayer %s\n" % myID).encode())
        client.send(("newPlayer %s\n" % cID).encode())
    clientele[myID] = client
    client.send(("myIDis %s \n" % myID).encode())
    print("connection recieved from %s" % myID)
    threading.Thread(target = handleClient,
                    args = (client, serverChannel, myID, clientele)).start()
    playerNum += 1










