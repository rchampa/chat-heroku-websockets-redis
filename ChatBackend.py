# -*- coding: utf-8 -*-

class ChatBackend(object):
    """Interface for registering and updating WebSocket clients."""

    def __init__(self,redis,redis_chan,gevent,app):
        self.gevent = gevent
        self.app = app
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(redis_chan)


    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                self.app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            for client in self.clients:
                self.gevent.spawn(self.send, client, data)

    def start(self):
        """Maintains Redis subscription in the background."""
        self.gevent.spawn(self.run)

