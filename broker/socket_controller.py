import logging
import os
import socket
import json

from jwt_controller import SecurityCell
from concurrent.futures import ThreadPoolExecutor
from cache_controller import CacheController


class SocketController:
    __instance = None
    __port = 0
    __host = ''
    __connection_pool = []
    __connections = []

    __security = SecurityCell().__get_instance__
    __cache = CacheController()

    s = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @property
    def instance(self):
        if self.__instance is None:
            self.__instance = object.__new__(self)
        return self.__instance

    def configure(self, host, port):
        """
        Configure the host for the new broker
        :param host: Personalize host for the server. Environment has more relevance
        :param port: Personalize port for the server. Environment has more relevance
        :return:
        """
        logging.basicConfig(level=logging.DEBUG, format='%(threadName)s: %(message)s')
        self.__port = os.environ.get("PORT", port)
        self.__host = os.environ.get("HOST", host)
        self.s = socket.create_server(("", 5050))
        self.s.listen(5)
        logging.info(f"Server configure in {self.__host}:{self.__port}")

    def start_socket(self):
        executor = ThreadPoolExecutor()

        while True:
            connection, address = self.s.accept()
            # Verify loggin
            connection_auth = connection.recv(4096)
            auth_result, key = self.auth(connection_auth)
            if auth_result:
                logging.info(f"Connection accepted from: {address} pining back")
                pinning = {
                    "type": "response",
                    "response": "welcome"
                }
                connection.send(self.__security.generate_token(pinning, key).encode())

                data = json.loads(connection_auth.decode())
                if data['topic'] == "update" and data['from'] == "synchronizer":
                    executor.submit(self.__update_connection, connection, address, key)
                else:
                    executor.submit(self.__read_connection, connection, address)
            else:
                logging.error("Authentication failed")
                pinning = {
                    "type": "error",
                    "response": "Authentication failed"
                }
                connection.send(self.__security.generate_token(pinning, key).encode())

    def auth(self, connection_auth):
        data = json.loads(connection_auth.decode())
        if data['type'] == "connection":
            if data['topic'] == "update":
                if data["from"] == "synchronizer" and data['user'] == "channel_controller":
                    return True, data['defaultKey']
                else:
                    return False, None
            else:
                logging.info(self.__cache.search_client(data['user']))
                return True,
        else:
            return False, None

    def __update_connection(self, connection, address, key):
        while True:
            data = connection.recv(4096)

            if not data:
                connection.close()

            data = data.decode()
            logging.info(data)

            _key = {'k': key, 'kty': 'oct'}
            try:
                info_to_update = self.__security.verify_token(data, _key)
            except Exception as err:
                logging.error(err)

            self.__cache.save(info_to_update['data'])

            response = json.dumps({
                    "type": "response",
                    "response": "synchronized"
                }).encode()

            response = self.__security.generate_token(response, key)

            try:
                connection.send(response.encode())
            except Exception as err:
                logging.info("Thread killed. Connection closed")
                logging.error(err)

    def __read_connection(self, connection, address):
        while True:
            data = connection.recv(4096)

            if not data:
                connection.close()

            data = data.decode()
            logging.info(data)

            if data == "close":
                connection.send("Connection closed".encode())
                connection.close()
                break

            try:
                connection.send(data.encode())
            except Exception as err:
                logging.info("Thread killed. Connection closed")
                logging.error(err)

    def create_new_client(self):
        pass

    def __attach_client_in_topic(self, connection, address, topic):
        pass