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
            redis.publish(REDIS_CHAN, message)


@sockets.route('/receive')
def outbox(ws):
    """Sends outgoing chat messages, via `ChatBackend`."""
    chats.register(ws)

    #while ws.socket is not None:
    while not ws.closed:
        # Context switch while `ChatBackend.start` is running in the background.
        gevent.sleep()
