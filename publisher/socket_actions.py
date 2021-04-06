import json
import logging
import os
import socket

from jwt_controller import SecurityCell
from flask import request, jsonify


class SocketActions:
    __instance = None
    __socket = None
    __security = SecurityCell().__get_instance__
    __user_key = {'k': os.environ.get('USER_KEY', "Byu502cUBiIFn_MtACnr69s9pbnqRT2WacuL28xUejc"), 'kty': 'oct'}
    __user = os.environ.get('SUSER', "3d63339eeb222943dc3161f114dcd4d7")

    __is_ready = False

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @property
    def __get_instance__(self):
        if self.__instance is None:
            self.__instance = object.__new__(self)
        return self.__instance

    def start_socket(self):
        if self.__user is None or self.__user == "":
            raise Exception("No se ha encontrado ningun usuario agregalo al entorno")

        if self.__user_key['k'] is None or self.__user_key['k'] == "":
            raise Exception("No se han encontrado la llave ingresa la variable de entorno")

        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect(('34.192.83.53', 5050))
        data = {
            "type": "connection",
            "from": socket.gethostname(),
            "user": self.__user,
            "topic": ""
        }
        self.__socket.sendall(json.dumps(data).encode())
        data = self.__socket.recv(4096)
        data = data.decode()
        data = self.__security.verify_token(data, self.__user_key)

        if data['response'] == "welcome":
            self.__is_ready = True

    def new_message(self):
        if not self.__is_ready:
            raise Exception("Error connection is not opened")

        request_data = request.get_json()
        try:
            request_data = self.__security.verify_token(request_data['payload'], self.__user_key)
        except:
            return jsonify({
                "type": "error",
                "error": "Authentication failed",
            }), 401

        data = {
            "type": "message",
            "from": socket.gethostname(),
            "user": self.__user,
            "topic": request_data['topic'],
            "message": request_data['message']
        }

        data = self.__security.generate_token(data, self.__user_key['k'])

        try:
            self.__socket.sendall(data.encode())
        except:
            raise Exception("Error connection is not opened")

        data = self.__socket.recv(4096)
        logging.info(data.decode())
        return jsonify({
            "type": "response",
            "response": "All done"
        })

    def disconnect(self):
        if not self.__is_ready:
            raise Exception("Error connection is not opened")

        request_data = request.get_json()
        if request_data['user'] != self.__user:
            return jsonify({
                "type": "error",
                "error": "Authentication failed",
            }), 401

        data = {
            "type": "disconnect",
            "from": socket.gethostname(),
            "user": self.__user,
            "topic": "",
            "message": ""
        }

        data = self.__security.generate_token(data, self.__user_key['k'])

        try:
            self.__socket.sendall(data.encode())
        except:
            raise Exception("Error connection is not opened")

        data = self.__socket.recv(4096)
        logging.info(data.decode())
        return jsonify({
            "type": "response",
            "response": "All done"
        })
