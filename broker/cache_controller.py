import logging


class CacheController:
    __instance = None

    channels = []
    clients = []

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        return cls.__instance

    @property
    def __get_instance__(self):
        if self.__instance is None:
            self.__instance = object.__new__(self)
            return self.__instance
        return self.__instance

    def save(self, information):
        self.clients = information['clients']
        self.channels = information['channels']
        logging.info("Cache saved")

    def get(self):
        return self.clients, self.queues

    def search_client(self, id):
        logging.info(self.clients)
        return next((client for client in self.clients if client['_id'] == id), None)

