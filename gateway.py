'''
Simple API gateway, router, load balancer, and authenticator for the microblogging webservice.

Based on <https://github.com/ProfAvery/cpsc449/tree/master/bottle/gateway/gateway.py>
'''

import sys
import json
import http.client
import logging.config

import bottle
from bottle import route, request, response, get, auth_basic

import requests

from collections import deque


# Allow JSON values to be loaded from app.config[key]
#
def json_config(key):
    value = app.config[key]
    return json.loads(value)


# Set up app and logging
#
app = bottle.default_app()
app.config.load_config('./etc/gateway.ini')

logging.config.fileConfig(app.config['logging.config'])

# Setup Load balancer
timelineRotation = deque([{'address':addr, 'online':True} for addr in json_config('timelineService.upstreams')])


# If you want to see traffic being sent from and received by calls to
# the Requests library, add the following to etc/gateway.ini:
#
#   [logging]
#   requests = true
#
if json_config('logging.requests'):
    http.client.HTTPConnection.debuglevel = 1

    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    logging.debug('Requests logging enabled')


# Return errors in JSON
#
# Adapted from <https://stackoverflow.com/a/39818780>
#
def json_error_handler(res):
    if res.content_type == 'application/json':
        return res.body
    res.content_type = 'application/json'
    if res.body == 'Unknown Error.':
        res.body = bottle.HTTP_CODES[res.status_code]
    return bottle.json_dumps({'error': res.body})


app.default_error_handler = json_error_handler


# Disable warnings produced by Bottle 0.12.19 when reloader=True
#
# See
#  <https://docs.python.org/3/library/warnings.html#overriding-the-default-filter>
#
if not sys.warnoptions:
    import warnings
    warnings.simplefilter('ignore', ResourceWarning)


def getTimelineServer():
    '''Returns an address/port from the timeline service pool using a Round Robin Policy'''

    # Pop from queue and re-add to end of queue
    tls = first = timelineRotation.popleft()
    timelineRotation.append(tls)

    # Skip over any that are "offline"
    while not tls['online']:
        tls = timelineRotation.popleft()
        timelineRotation.append(tls)

        # Check if looped through all
        if tls == first:
            return False

    return tls['address']


def removeTimelineServer(address):
    '''Marks matching address/port in the timeline service pool as "offline"'''

    tls = first = timelineRotation.popleft()

    # Loop until entry with matching address is found
    while tls['address'] != address:
        timelineRotation.append(tls)
        tls = timelineRotation.popleft()

        # Check if looped through all, shouldn't occur but just to be safe
        if tls == first:
            return False

    tls['online'] = False
    timelineRotation.append(tls)


def authenticateUser(username, password):
    '''Authentication function for the @auth_basic decorator'''

    # Route to user service
    upstream_server = json_config('userService.upstream')

    #Send request to user service to check password/credentials
    r = requests.get(url = '{}/users/{}?password={}'.format(upstream_server, username, password))

    # get boolean from the response
    result = r.json()['authenticated']

    return result
    

def gateway(mthd, url, dt, hdrs, cks):
    '''Constructs and sends an HTTP Request and returns the response'''

    try:
        upstream_response = requests.request(
            mthd,
            url,
            data=dt,
            headers=hdrs,
            cookies=cks,
            stream=True,
        )
    except requests.exceptions.RequestException as e:
        logging.exception(e)
        response.status = 503
        return {
            'method': e.request.method,
            'url': e.request.url,
            'exception': type(e).__name__,
        }

    response.status = upstream_response.status_code
    for name, value in upstream_response.headers.items():
        if name.casefold() == 'transfer-encoding':
            continue
        response.set_header(name, value)
    return upstream_response


@route('/users/<:re:.*>', method='ANY')
@auth_basic(authenticateUser)
@route('/users/<>', method='GET')   # Bypasses authentication for the user service checkPassword()
def userService():
    '''Routes and authenticates most requests to the user service'''

    path = request.urlparts._replace(scheme='', netloc='').geturl()

    # Get route/path to user service
    upstream_server = json_config('userService.upstream')

    upstream_url = upstream_server + path
    logging.debug('Upstream URL: %s', upstream_url)

    headers = {}
    for name, value in request.headers.items():
        if name.casefold() == 'content-length' and not value:
            headers['Content-Length'] = '0'
        else:
            headers[name] = value

    # Requested information passed to gateway
    # Response Content from the gateway's request is returned
    return gateway(request.method, upstream_url, request.body, headers, request.cookies).content


@route('/posts/<:re:.*>', method='ANY')
@auth_basic(authenticateUser)
def timelineService():
    '''Routes and authenticates most requests to the timeline service'''

    path = request.urlparts._replace(scheme='', netloc='').geturl()

    # Get route/path to a timeline service
    upstream_server = getTimelineServer()

    # If all timeline services are down
    if not upstream_server:
        response.status = 503
        return b'HTTP/1.1 503 Service Unavailable'

    upstream_url = upstream_server + path
    logging.debug('Upstream URL: %s', upstream_url)

    headers = {}
    for name, value in request.headers.items():
        if name.casefold() == 'content-length' and not value:
            headers['Content-Length'] = '0'
        else:
            headers[name] = value

    # Requested information passed to gateway
    resp = gateway(request.method, upstream_url, request.body, headers, request.cookies)

    # Check if a timeline service is down
    if resp.status_code >= 500:
        removeTimelineServer(upstream_server)

    # Response Content from the gateway's request is returned
    return resp.content


@route('/messages/<:re:.*>', method='ANY')
@auth_basic(authenticateUser)
def messageService():
    '''Routes and authenticates all requests to the message service'''

    path = request.urlparts._replace(scheme='', netloc='').geturl()

    # Get route/path to message service
    upstream_server = json_config('messageService.upstream')

    upstream_url = upstream_server + path
    logging.debug('Upstream URL: %s', upstream_url)

    headers = {}
    for name, value in request.headers.items():
        if name.casefold() == 'content-length' and not value:
            headers['Content-Length'] = '0'
        else:
            headers[name] = value

    # Requested information passed to gateway
    # Response Content from the gateway's request is returned
    return gateway(request.method, upstream_url, request.body, headers, request.cookies).content


@route('/index/<:re:.*>', method='ANY')
# @auth_basic(authenticateUser)
def searchEngineService():
    '''Routes and authenticates all requests to the search service'''

    path = request.urlparts._replace(scheme='', netloc='').geturl()

    # Get route/path to search engine service
    upstream_server = json_config('searchEngineService.upstream')

    upstream_url = upstream_server + path
    logging.debug('Upstream URL: %s', upstream_url)

    headers = {}
    for name, value in request.headers.items():
        if name.casefold() == 'content-length' and not value:
            headers['Content-Length'] = '0'
        else:
            headers[name] = value

    # Requested information passed to gateway
    # Response Content from the gateway's request is returned
    return gateway(request.method, upstream_url, request.body, headers, request.cookies).content


@get('/home/<username>')
@auth_basic(authenticateUser)
def getHomeTimeline(username):
    '''Handles and authenticates requests for home timeline'''

    # Get route/path to user service and a timeline service
    user_server = json_config('userService.upstream')
    timeline_server = getTimelineServer()

    user_url = '{}/users/{}/followings/'.format(json_config('userService.upstream'), username)
    timeline_url = '{}/posts/followings/'.format(getTimelineServer())

    # If all timeline services are down
    if not timeline_server:
        response.status = 503
        return b'HTTP/1.1 503 Service Unavailable'

    #Send request for the following list from the user service
    resp = requests.get(url = user_url)

    #Retrieve list of usernames, that the provided user is following
    following = resp.json().get('following')
    #Format to an easier query string for the timeline service
    dt = {'following':json.dumps([e[0] for e in following])}

    #Send request with list of usernames to timeline service
    resp = requests.get(url = timeline_url, params = dt)

    # Check if a timeline service is down
    if resp.status_code >= 500:
        removeTimelineServer(timeline_server)

    return resp.content

