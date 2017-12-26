###############################################################################
# lets users create a username and login to an account
###############################################################################

import sqlite3
import time
import sys

# adpated from terminal based and changed paramaters 
# video by
# Advice4u99
# https://www.youtube.com/watch?v=hW741TsBZag

def login(username, password):
    # enter username and pswd
    # check if exists, login if exists
    # if wrong, retry?
    with sqlite3.connect("users.db") as db:
        cursor = db.cursor()
    # check if exists in database
    findUser = ("SELECT * FROM user WHERE username = ? AND \
                 password = ?")
    cursor.execute(findUser, [(username),(password)])
    results = cursor.fetchall()

    if results:
        for i in results:
            print("Welcome " + i[2])

    print("failed")

    return results

def loginCheck(username, password):

    with sqlite3.connect("users.db") as db:
        cursor = db.cursor()
    # check if exists in database
    findUser = ("SELECT * FROM user WHERE username = ? AND \
                 password = ?")
    cursor.execute(findUser, [(username),(password)])
    results = cursor.fetchall()

    return results



def newUser(username, password):
    with sqlite3.connect("users.db") as db:
        cursor = db.cursor()
    findUser = ("SELECT * FROM user WHERE username = ?")
    cursor.execute(findUser, [(username)])


    firstname = username
    lastname = password


    insertData = """ INSERT INTO user(username, firstname, lastname, password)
    VALUES(?,?,?,?) """
    cursor.execute(insertData, [(username), (firstname), (lastname),\
     (password)])
    db.commit()



