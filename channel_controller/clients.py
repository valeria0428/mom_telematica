from flask import request, jsonify

from jwcrypto.jws import InvalidJWSSignature
from jwt_controller import JWTController

from storage_controller import StorageController
from synchronizer import Synchronizer

import logging
import json
import time


class Clients:
    __JWT = JWTController().__get_instance__
    __storage = StorageController().__get_instance__
    __sync = Synchronizer().__get_instance__

    def add_user(self):
        data = request.get_json()
        payload = data['payload']
        key = json.loads(self.__JWT.get_global_key)

        try:
            deserialized_data = self.__JWT.verify_token(payload, key)
        except InvalidJWSSignature as signErr:
            logging.error(f"Error in the verification {signErr}")
            return jsonify({
                "type": "error",
                "payload": self.__JWT.generate_token({
                    "type": "error",
                    "msg": "Error en la validación de la firma digital",
                    "system_msg": signErr.args
                }, key['k']),
                "time": time.time()
            }), 401
        except Exception as err:
            logging.error(err)
            return jsonify({
                "type": "error",
                "payload": self.__JWT.generate_token({
                    "type": "Unrecognized error",
                    "msg": err.args
                }, key['k']),
                "time": time.time()
            }), 401

        logging.debug(f"New user received {deserialized_data['name']}")

        key_for_user = self.__JWT.generate_new_symmetric_key()
        user = {
            "name": deserialized_data['name'],
            "key": json.loads(key_for_user),
            "created_time": time.time()
        }

        user = self.__storage.insert(user, self.__storage.db_clients)
        self.__sync.update()
        return jsonify({
            "type": "response",
            "payload": self.__JWT.generate_token(user, key['k']),
            "time": time.time()
        }), 200

    def delete_user(self, user):
        payload = user
        key = json.loads(self.__JWT.get_global_key)

        try:
            deserialized_data = self.__JWT.verify_token(payload, key)
        except InvalidJWSSignature as signErr:
            logging.error(f"Error in the verification {signErr}")
            return jsonify({
                "type": "error",
                "payload": self.__JWT.generate_token({
                    "type": "error",
                    "msg": "Error en la validación de la firma digital",
                    "system_msg": signErr.args
                }, key['k']),
                "time": time.time()
            }), 401
        except Exception as err:
            logging.error(err)
            return jsonify({
                "type": "error",
                "payload": self.__JWT.generate_token({
                    "type": "Unrecognized error",
                    "msg": err.args
                }, key['k']),
                "time": time.time()
            }), 401

        id = deserialized_data['id']

        self.__storage.delete(id, self.__storage.db_clients)
        self.__sync.update()
        return jsonify({
            "type": "response",
            "payload": self.__JWT.generate_token({
                "time": time.time(),
                "deleted": id
            }, key['k']),
            "time": time.time()
        }), 200

    def get_all_users(self):
        return jsonify(self.__storage.get_all_documents(self.__storage.db_clients))

    def get_user(self, user):
        payload = user
        key = json.loads(self.__JWT.get_global_key)

        try:
            deserialized_data = self.__JWT.verify_token(payload, key)
        except InvalidJWSSignature as signErr:
            logging.error(f"Error in the verification {signErr}")
            return jsonify({
                "type": "error",
                "payload": self.__JWT.generate_token({
                    "type": "error",
                    "msg": "Error en la validación de la firma digital",
                    "system_msg": signErr.args
                }, key['k']),
                "time": time.time()
            }), 401
        except Exception as err:
            logging.error(err)
            return jsonify({
                "type": "error",
                "payload": self.__JWT.generate_token({
                    "type": "Unrecognized error",
                    "msg": err.args
                }, key['k']),
                "time": time.time()
            }), 401

        try:
            return jsonify({
                "type": "response",
                "payload": self.__JWT.generate_token(self.__storage.search(deserialized_data['id'],
                                                                           self.__storage.db_clients), key['k']),
                "time": time.time()
            })
        except IndexError as err:
            logging.error(err)
            return jsonify({
                "type": "error",
                "payload": self.__JWT.generate_token({
                    "type": "Error",
                    "msg": "Id not founded"
                }, key['k']),
                "time": time.time()
            })
