#!/usr/bin/env python3

# Microblogging - Timeline Service API

import bottle
from bottle import post, get, request, HTTPResponse
import sqlite3
import json
import requests

# Setup app
app = bottle.default_app()


@get('/posts/<username>/')
def getUserTimeline(username):
    '''Returns latest 25 posts a user'''

    result = {}
    headers = {'Content-type': 'application/json'}

    #Connect to Database
    con = sqlite3.connect('posts.db')
    cur = con.cursor()
    
    #Query database for posts with the given username
    u = (username,)
    result = []
    for row in cur.execute('SELECT * FROM posts WHERE user_id=? ORDER BY timestamp DESC LIMIT 25', u):
        result.append(row)
        
    con.close()
    return HTTPResponse(body=json.dumps({'userTimeline':result}),status=200,headers=headers)


@get('/posts/')
def getPublicTimeline():
    '''Returns latest 25 posts in the post database'''

    result = {}
    headers = {'Content-type': 'application/json'}

    #Connect to Database
    con = sqlite3.connect('posts.db')
    cur = con.cursor()
    
    result = []
    for row in cur.execute('SELECT * FROM posts ORDER BY timestamp DESC LIMIT 25'):
        result.append(row)
    
    con.close()
    return HTTPResponse(body=json.dumps({'publicTimeline':result}),status=200,headers=headers)


@get('/posts/followings/')
def getFollowingTimeline():
    '''Returns latest 25 posts from users provided in the query list'''
    
    result = {}
    headers = {'Content-type': 'application/json'}

    #Retrieve list of usernames, that the provided user is following
    following = json.loads(request.query.following)

    if type(following) is not list:
        result['status'] = "400 Bad Request"
        result['error'] = 'Query "following" does not contain a list'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    
    #Format string of following to give to query
    string = ''
    for user in following:
        string += "'{}',".format(user)
    string = string[:-1]
    
    #Connect to Database
    con = sqlite3.connect('posts.db')
    cur = con.cursor()
    
    #Query for posts.db
    result = []
    for row in cur.execute('SELECT * FROM posts WHERE user_id IN ({}) ORDER BY timestamp DESC LIMIT 25'.format(string)):
        result.append(row)
        
    #print(result)
    con.close()
    return HTTPResponse(body=json.dumps({'homeTimeline':result}),status=200,headers=headers)


@post('/posts/')
def postTweet():
    '''Creates a post entry in the posts database'''

    result = {}
    headers = {'Content-type': 'application/json'}

    #Retrieve JSON data
    body = request.json
    username = body['username']
    text = body['text']

    if type(username) is not str:
        result['status'] = "400 Bad Request"
        result['error'] = 'JSON entry "username" does not contain a string'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    if type(text) is not str:
        result['status'] = "400 Bad Request"
        result['error'] = 'JSON entry "text" does not contain a string'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)
    
    #Connect to Database
    con = sqlite3.connect('posts.db')
    cur = con.cursor()
    
    #Add userToFollow to following table at username
    entry = (username, text)
    cur.execute("INSERT INTO posts(user_id, text, timestamp) VALUES (?,?,datetime('now'))", entry)
    post_id = cur.lastrowid
    con.commit()
    con.close()

    # Create inverted index entry for the post
    dt = {'postId':post_id, 'text':text}
    r = requests.post('http://localhost:5400/index/', json=dt)

    return HTTPResponse(body=json.dumps({'posted':True}),status=200,headers=headers)

