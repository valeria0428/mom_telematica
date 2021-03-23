from cache_controller import CacheController
import logging


class TopicsManager:
    subscribers_controller = []
    __cache = CacheController().__get_instance__

    def __init__(self):
        self.update()

    def add_subscriber(self, channel, subscriber_connection):
        _channel = next((__channel for __channel in self.subscribers_controller if __channel['channel'] == channel),
                        None)
        if not _channel:
            raise Exception("Channel not founded")

        (_channel['subscribers']).append(subscriber_connection)
        return True

    def send_message_to_subscribers(self, channel, address, message):
        _channel = next((__channel for __channel in self.subscribers_controller if __channel['channel'] == channel),
                        None)

        if not _channel:
            logging.error("Channel not found")
            raise Exception("Channel not founded")

        for __channel in _channel['subscribers']:
            try:
                __channel.send(message.encode())
            except:
                pass

    def update(self):
        _, channels = self.__cache.get()

        self.subscribers_controller = [{
            'channel': channel['_id'],
            'subscribers': []
        } for channel in channels]
