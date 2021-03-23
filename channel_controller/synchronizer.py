import socket
import json
import time
import logging
import threading

from jwt_controller import JWTController
from storage_controller import StorageController


class Synchronizer:
    __instance = None
    __socket = None
    __watcher_thread = None
    __watcher_execution = True

    last_update = 0

    __JWT = JWTController().__get_instance__
    __storage = StorageController().__get_instance__

    is_connected = False

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

    def connect(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect(('34.192.83.53', 5050))

        key = json.loads(self.__JWT.get_global_key)

        logging.info("Connected to the broker server in 0.0.0.0:5050")

        enable_connection = {
            "type": "connection",
            "from": "synchronizer",
            "user": "channel_controller",
            "topic": "update",
            "defaultKey": key['k']
        }

        self.__socket.sendall(json.dumps(enable_connection).encode())
        data = self.__socket.recv(4096)
        decrypted = self.__JWT.verify_token(data.decode(), key)
        if decrypted['type'] == "response":
            if decrypted['response'] == "welcome":
                self.is_connected = True
                send = {
                    "type": "synchronize",
                    "from": "synchronizer",
                    "user": "channel_controller",
                    "topic": "updated",
                    "data": {
                        "channels": self.__storage.get_all_documents(self.__storage.db_channels),
                        "clients": self.__storage.get_all_documents(self.__storage.db_clients)
                    }
                }
                self.__socket.sendall(self.__JWT.generate_token(send, key['k']).encode())
                data = self.__socket.recv(4096)
                data = self.__JWT.verify_token(data.decode(), key)
                if data['response'] == "synchronized":
                    self.last_update = time.time()
                    logging.info("Broker information updated successfully")
                else:
                    logging.error("Error updated the broker try to run the method updated to solve this problem")
            else:
                logging.error(decrypted['response'])
        else:
            logging.error(decrypted['response'])

    def start_watcher(self):
        self.__watcher_thread = threading.Thread(target=self.__watcher__, name="checker")
        self.__watcher_thread.start()
        logging.info("Checker started")

    def stop_watcher(self):
        self.__watcher_execution = False
        self.__watcher_thread.join()
        return True

    def __watcher__(self):
        while self.__watcher_execution:
            logging.info("Checking connection")
            try:
                data = {
                    "type": "ping",
                    "defaultKey": self.__JWT.get_global_key
                }

                key = json.loads(self.__JWT.get_global_key)

                data = self.__JWT.generate_token(data, key['k'])

                self.__socket.sendall(data.encode())

                response = self.__socket.recv(4096)

                try:
                    response = self.__JWT.verify_token(response.decode(), {'k': key['k'], 'kty': 'oct'})
                except:
                    continue

                if response['response'] == "pong":
                    logging.info(f"Broker connected {time.time()}")
            except:
                logging.info("Server don't pong, resync")
                self.is_connected = False
                try:
                    self.connect()
                except:
                    pass

            time.sleep(5)

    def update(self):
        if self.is_connected:
            key = json.loads(self.__JWT.get_global_key)

            logging.info(f"Last time of a update is: {self.last_update}")
            logging.info("Updating broker information")

            send = {
                "type": "synchronize",
                "from": "synchronizer",
                "user": "channel_controller",
                "topic": "updated",
                "data": {
                    "channels": self.__storage.get_all_documents(self.__storage.db_channels),
                    "clients": self.__storage.get_all_documents(self.__storage.db_clients),
                }
            }
            self.__socket.sendall(self.__JWT.generate_token(send, key['k']).encode())
            data = self.__socket.recv(4096)
            data = self.__JWT.verify_token(data.decode(), key)
            if data['response'] == "synchronized":
                self.last_update = time.time()
                logging.info("Broker information updated successfully")
            else:
                logging.error("Error updated the broker try to run the method updated to solve this problem")
        else:
            logging.error("Error updating the broker connection is not enabled")
