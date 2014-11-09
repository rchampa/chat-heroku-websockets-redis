# -*- coding: utf-8 -*-

"""
Chat Server
===========
This simple application uses WebSockets to run a primitive chat server.
"""

import os
import logging
import redis
import gevent
from flask import Flask, render_template
from flask_sockets import Sockets

from constants import REDIS_URL,REDIS_CHANNEL

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

sockets = Sockets(app)
myredis = redis.from_url(REDIS_URL)

from ChatBackend import ChatBackend
chats = ChatBackend(myredis,REDIS_CHANNEL,gevent,app)
chats.start()

@app.route('/')
def hello():
    return render_template('index.html')


@sockets.route('/submit')
def inbox(ws):
    """Receives incoming chat messages, inserts them into Redis."""
    #while ws.socket is not None:
    while not ws.closed:
        # Sleep to prevent *contstant* context-switches.
        gevent.sleep()
        message = ws.receive()

        if message:
            app.logger.info(u'Inserting message: {}'.format(message))
            myredis.publish(REDIS_CHANNEL, message)


@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    print "register"
    chats.register(ws)

    #while ws.socket is not None:
    while not ws.closed:
        #print "receive2"
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep()


