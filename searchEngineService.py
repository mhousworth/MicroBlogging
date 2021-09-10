#!/usr/bin/env python3

# Microblogging - Search Engine MicroService API

import bottle
from bottle import post, get, request, HTTPResponse
import json
import re

import redis


# Setup app
app = bottle.default_app()

def getTokens(keywords: str):

    # Casefold string
    keywords = keywords.casefold()
    # Replace all punctuation with whitespace
    keywords = re.sub(r'[^\w\s]', ' ', keywords)
    # Tokenize string, Convert to a Set, Remove stopwords
    tokens = rmStopWords(set(keywords.split()))

    return tokens

# Returns a set of tokens with stopwords removed
def rmStopWords(tokens: set):

    # Retrieve list of stopwords from JSON file
    f = open('stopwords.json',)
    data = json.load(f)
    stopwords = set(data['StopWords'])

    f.close()

    # Difference includes all token that do not match with stopwords
    return tokens.difference(stopwords)


@post('/index/')
def index():

    result = {}
    headers = {'Content-type': 'application/json'}

    # Retrieve JSON data
    body = request.json
    post_id = body['postId']
    text = body['text']

    # Validate JSON data
    if type(post_id) is not int:
        result['status'] = "400 Bad Request"
        result['error'] = 'JSON entry "postId" does not contain an int'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    if type(text) is not str:
        result['status'] = "400 Bad Request"
        result['error'] = 'JSON entry "text" does not contain a string'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    # Extract Tokens
    tokens = getTokens(text)
    pid = str(post_id)

    # Connect to Redis
    redisClient = redis.Redis(host='localhost', port=6379, db=0)

    # For every token t
    for t in tokens:
        # Insert value post id
        redisClient.sadd(t, pid)

    headers = {'Content-type': 'application/json'}

    return HTTPResponse(body=json.dumps({'indexed':True}),status=200,headers=headers)
    

@get('/index/search')
def search():

    result = {}
    headers = {'Content-type': 'application/json'}

    # Get query
    keyword = request.query.keyword

    # Extract Tokens
    tokenSet = getTokens(keyword)

    # Validate string contains one token
    print(tokenSet)
    if len(tokenSet) != 1:
        result['status'] = "400 Bad Request"
        result['error'] = 'query entry "keyword" contains a string with more than one token'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    if len(tokenSet) == 0:
        result['status'] = "400 Bad Request"
        result['error'] = 'query entry "keyword" contains a stopword, too common for search parameter'
        return HTTPResponse(body=json.dumps(result),status=400,headers=headers)

    # Extract Token
    token = tokenSet.pop()

    # Connect to Redis
    redisClient = redis.Redis(host='localhost', port=6379, db=0)

    # Retrieve number of elements by the range of the key's cardinality
    result = redisClient.smembers(token)
    
    # Converts list of btye strings to integers, then sorts it
    result = [int(r.decode('utf-8')) for r in result]
    result = sorted(result)

    return HTTPResponse(body=json.dumps({'found':result}),status=200,headers=headers)


@get('/index/search-any')
def any():
    
    result = {}
    headers = {'Content-type': 'application/json'}

    # Get query
    keywordList = request.query.keywordList

    # Extract Tokens
    tokenSet = getTokens(keywordList)


    # Connect to Redis
    redisClient = redis.Redis(host='localhost', port=6379, db=0)

    # Retrieve list of all post id values that include any provided keys/tokens
    result = redisClient.sunion(tokenSet)

    # Converts list of btye strings to integers, then sorts it
    result = [int(r.decode('utf-8')) for r in result]
    result = sorted(result)

    return HTTPResponse(body=json.dumps({'found':result}),status=200,headers=headers)


@get('/index/search-all')
def all():
    
    result = {}
    headers = {'Content-type': 'application/json'}

    # Get query
    keywordList = request.query.keywordList

    # Extract Tokens
    tokenSet = getTokens(keywordList)


    # Connect to Redis
    redisClient = redis.Redis(host='localhost', port=6379, db=0)

    # Retrieve list of post id values that include all provided keys/tokens
    result = redisClient.sinter(tokenSet)

    # Converts list of btye strings to integers, then sorts it
    result = [int(r.decode('utf-8')) for r in result]
    result = sorted(result)

    return HTTPResponse(body=json.dumps({'found':result}),status=200,headers=headers)


@get('/index/search-exclude')
def exclude():
    
    result = {}
    headers = {'Content-type': 'application/json'}

    # Get queries
    includeList = request.query.includeList
    excludeList = request.query.excludeList

    # Extract include Tokens
    includeSet = getTokens(includeList)

    # Extract exclude Tokens
    excludeSet = getTokens(excludeList)


    # Connect to Redis
    redisClient = redis.Redis(host='localhost', port=6379, db=0)

    # For the include and exclude token sets
    # Create a new set of post id values that include all provided keys/tokens
    redisClient.sunionstore(dest='?include', keys=includeSet)
    redisClient.sunionstore(dest='?exclude', keys=excludeSet)

    # Retrieve a list that includes posts ids from the include set and not in the excludes set
    result = redisClient.sdiff('?include', '?exclude')

    # Clear the include and exclude sets from Redis
    icard = redisClient.scard('?include')
    redisClient.spop('?include', count=icard)
    ecard = redisClient.scard('?exclude')
    redisClient.spop('?exclude', count=ecard)

    # Converts list of btye strings to integers, then sorts it
    result = [int(r.decode('utf-8')) for r in result]
    result = sorted(result)

    return HTTPResponse(body=json.dumps({'found':result}),status=200,headers=headers)

