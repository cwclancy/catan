# does the randomness, shuffling deck and hadling die roll
import math, random

def rollDie():
    return random.randint(1,6)

def randomList(L):
    newOrder = random.sample(range(len(L)), len(L))
    randomList = [0]*len(L)
    for i in range(len(L)):
        randomList[newOrder[i]] = L[i]
    return randomList




