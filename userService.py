#!/usr/bin/env python3

# Microblogging - User Service API

import bottle
from bottle import post, get, request, delete, HTTPResponse
import sqlite3
import json

# Setup app
app = bottle.default_app()


@post('/users/')
def createUser():
    '''Adds a user account to the users database'''

    headers = {'Content-type': 'application/json'}

    #Retrieve JSON data
    body = request.json
    username = body['username']
    password = body['password']
    email = body['email']

    #Connect to Database
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    
    #Query Database for matching username
    u = (username,)
    cur.execute("SELECT * FROM users WHERE user_id=?", u)
    if cur.fetchone() is None:
        #Create user entry
        user = (username, password, email)
        cur.execute("INSERT INTO users VALUES (?,?,?)", user)
        con.commit()
        con.close()
        return HTTPResponse(body=json.dumps({'created':True}),status=201,headers=headers)
    else:
        con.close()
        result = {}
        result['created'] = False
        result['status'] = "409 Conflict"
        result['error'] = 'An account with this username already exists'
        return HTTPResponse(body=json.dumps(result),status=409,headers=headers)


@get('/users/<username>')
def checkPassword(username):
    '''Verifies username/password pair'''

    headers = {'Content-type': 'application/json'}

    password = request.query.password

    #Connect to Database
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    
    #Query database for a username & password match
    t = (username,password,)
    cur.execute("SELECT * FROM users WHERE user_id=? AND password=?", t)
    
    result = not cur.fetchone() is None
    con.close()
    return HTTPResponse(body=json.dumps({'authenticated':result}),status=200,headers=headers)


@post('/users/<username>/followings/')
def addFollower(username):
    '''Add a following entry to the users database'''

    headers = {'Content-type': 'application/json'}

    body = request.json
    followFlag = body['follow']
    
    if followFlag:
        userToFollow = body['usernameToFollow']
        
        #Connect to Database
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        
        #Add userToFollow to following table at username
        entry = (username, userToFollow)
        cur.execute("INSERT INTO followers VALUES (?,?)", entry)
        con.commit()
        con.close()
        return HTTPResponse(body=json.dumps({'followed':True}),status=200,headers=headers)


@delete('/users/<username>/followings/')
def removeFollower(username):
    '''Remove a following entry from the users database'''

    headers = {'Content-type': 'application/json'}

    body = request.json
    followFlag = body['follow']
    
    if not followFlag:
        userToRemove = body['usernameToRemove']
        
        #Connect to Database
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        
        #Remove follower entry
        t = (username,userToRemove,)
        cur.execute("DELETE FROM followers WHERE user_id=? AND follow_id=?", t)
        con.commit()
        con.close()
        return HTTPResponse(body=json.dumps({'followed':False}),status=200,headers=headers)


@get('/users/<username>/followings/')
def getFollowings(username):
    '''Retrieve a list of users followed from the users database'''

    headers = {'Content-type': 'application/json'}

    #Connect to Database
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    
    #Query database for a username & get list of users followed
    t = (username,)
    result = []
    for row in cur.execute("SELECT follow_id FROM followers WHERE user_id=?", t):
        result.append(row)
    
    return HTTPResponse(body=json.dumps({'following':result}),status=200,headers=headers)

