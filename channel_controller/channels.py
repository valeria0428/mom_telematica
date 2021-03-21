import logging
import time

from flask import request, jsonify
from jwcrypto.jws import InvalidJWSSignature

from jwt_controller import JWTController
from storage_controller import StorageController
from synchronizer import Synchronizer


class Channels:
    __storage = StorageController().__get_instance__
    __JWT = JWTController().__get_instance__
    __sync = Synchronizer().__get_instance__

    def __retrieve_user__(self, id):
        try:
            user = self.__storage.search(id, self.__storage.db_clients)
            return user, user['key']
        except IndexError as err:
            logging.error(err)
            return err

    def add_channel(self):
        data = request.get_json()
        payload = data['payload']
        try:
            user, key = self.__retrieve_user__(data['user'])
        except Exception as e:
            return jsonify({
                "type": "Authentication error",
                "msg": "User not founded"
            }), 401

        try:
            deserialized_data = self.__JWT.verify_token(payload, key)
        except InvalidJWSSignature as signErr:
            logging.error(f"Error in the verification {signErr}")
            return jsonify({
                "type": "error",
                "msg": "Error verifying the token",
                "system_msg": signErr.args
            }), 401
        except Exception as err:
            logging.error(err)
            return jsonify({
                "type": "Unrecognized error",
                "msg": err.args
            }), 401

        data = {
            "owner": data['user'],
            "name": deserialized_data['name'],
            "creation_time": time.time(),
            "queues": []
        }

        channel = self.__storage.insert(data, self.__storage.db_channels)
        self.__sync.update()
        return jsonify({
            "type": "response",
            "payload": self.__JWT.generate_token(channel, key['k']),
            "time": time.time()
        }), 200

    def list_channels(self, user):
        try:
            user, key = self.__retrieve_user__(user)  # Encrypt response
        except Exception as e:
            return jsonify({
                "type": "Authentication error",
                "msg": "User not founded"
            }), 401

        channels = self.__storage.get_all_documents(self.__storage.db_channels)
        return jsonify({
            "type": "response",
            "payload": self.__JWT.generate_token({
                "reponse": channels
            }, key['k']),
            "time": time.time()
        }), 200

    def remove_channel(self, channel, user):
        try:
            user, key = self.__retrieve_user__(user)
        except Exception as e:
            return jsonify({
                "type": "Authentication error",
                "msg": "User not founded"
            }), 401

        try:
            deserialized_data = self.__JWT.verify_token(channel, key)
        except InvalidJWSSignature as signErr:
            logging.error(f"Error in the verification {signErr}")
            return jsonify({
                "type": "error",
                "msg": "Error en la verifying the token",
                "system_msg": signErr.args
            }), 401
        except Exception as err:
            logging.error(err)
            return jsonify({
                "type": "Unrecognized error",
                "msg": err.args
            }), 401

        channel = self.__storage.search(deserialized_data['id'], self.__storage.db_channels)

        if channel['owner'] != user['_id']:
            return jsonify({
                'type': "Authentication error",
                'msg': "You need be the owner of the channel to remove it "
            })

        id = self.__storage.delete(deserialized_data['id'], self.__storage.db_channels)
        self.__sync.update()
        return jsonify({
            "type": "response",
            "payload": self.__JWT.generate_token({
                "time": time.time(),
                "deleted": id
            }, key['k']),
            "time": time.time()
        }), 200

    def add_queue(self):
        data = request.get_json()
        payload = data['payload']
        try:
            user, key = self.__retrieve_user__(data['user'])
        except Exception as e:
            return jsonify({
                "type": "Authentication error",
                "msg": "User not founded"
            }), 401

        try:
            deserialized_data = self.__JWT.verify_token(payload, key)
        except InvalidJWSSignature as signErr:
            logging.error(f"Error in the verification {signErr}")
            return jsonify({
                "type": "error",
                "msg": "Error en la verifying the token",
                "system_msg": signErr.args
            }), 401
        except Exception as err:
            logging.error(err)
            return jsonify({
                "type": "Unrecognized error",
                "msg": err.args
            }), 401

        try:
            channel = self.__storage.search(deserialized_data['channel'], self.__storage.db_channels)
        except Exception as e:
            return jsonify({
                "type": "error",
                "msg": "Channel not found"
            }), 401

        channel['queues'].append({
            "name": deserialized_data['name'],
            "creation_time": time.time()
        })

        id = self.__storage.update(deserialized_data['channel'], {"queues": channel['queues']},
                                   self.__storage.db_channels)
        self.__sync.update()
        return jsonify({
            "type": "response",
            "payload": self.__JWT.generate_token({
                'edited': id,
                'time': time.time()
            }),
            "time": time.time()
        }), 200

    def list_queue(self, channel, user):
        try:
            user, key = self.__retrieve_user__(user)
        except Exception as e:
            return jsonify({
                "type": "Authentication error",
                "msg": "User not founded"
            }), 401

        try:
            deserialized_data = self.__JWT.verify_token(channel, key)
        except InvalidJWSSignature as signErr:
            logging.error(f"Error in the verification {signErr}")
            return jsonify({
                "type": "error",
                "msg": "Error en la verifying the token",
                "system_msg": signErr.args
            }), 401
        except Exception as err:
            logging.error(err)
            return jsonify({
                "type": "Unrecognized error",
                "msg": err.args
            }), 401

        channel = self.__storage.search(deserialized_data['channel'], self.__storage.db_channels)
        return jsonify({
            "type": "response",
            "payload": self.__JWT.generate_token({
                "response": channel['queues']
            }, key['k']),
            "time": time.time()
        }), 200

    def delete_queue(self, channel, user):
        try:
            user, key = self.__retrieve_user__(user)
        except Exception as e:
            return jsonify({
                "type": "Authentication error",
                "msg": "User not founded"
            }), 401

        try:
            deserialized_data = self.__JWT.verify_token(channel, key)
        except InvalidJWSSignature as signErr:
            logging.error(f"Error in the verification {signErr}")
            return jsonify({
                "type": "error",
                "msg": "Error en la verifying the token",
                "system_msg": signErr.args
            }), 401
        except Exception as err:
            logging.error(err)
            return jsonify({
                "type": "Unrecognized error",
                "msg": err.args
            }), 401

        channel = self.__storage.search(deserialized_data['channel'], self.__storage.db_channels)

        if channel['owner'] != user['_id']:
            return jsonify({
                'type': "Authentication error",
                'msg': "You need be the owner of the channel to remove a queue"
            })

        index = next((i for (i, d) in enumerate(channel['queues']) if d['name'] == deserialized_data['queue']), None)
        logging.debug(index)
        channel['queues'].pop(index)
        logging.debug(channel)

        id = self.__storage.update(channel['_id'], {'queues': channel['queues']}, self.__storage.db_channels)
        self.__sync.update()
        return jsonify({
            "type": "response",
            "payload": self.__JWT.generate_token({
                "deleted": id,
                "time": time.time()
            }, key['k']),
            "time": time.time()
        })
