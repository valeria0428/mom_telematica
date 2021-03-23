from flask_instance import FlaskInstance
from jwt_controller import JWTController
from synchronizer import Synchronizer

import logging

# Import http methods
from clients import Clients
from channels import Channels

clients = Clients()
channels = Channels()

logging.basicConfig(level=logging.DEBUG)  # Configure logging

# Configure flask
flask_app = FlaskInstance().__getinstance__
app = flask_app.get_app()

# Creating symmetric key for the server
jwt = JWTController().__get_instance__
jwt.set_global_key(jwt.generate_new_symmetric_key())
logging.info(f"Use the following key to encrypt the data in order to talk with this server in external connections: {jwt.get_global_key}")

syncker = Synchronizer().__get_instance__

# Configure endpoints
# Client endpoints
flask_app.add_endpoint('/user', "new_user", clients.add_user, ['post'])
flask_app.add_endpoint('/user/<user>', 'delete_user', clients.delete_user, ['delete'])
flask_app.add_endpoint('/users', 'get_all_users', clients.get_all_users, ['get'])
flask_app.add_endpoint('/user/<user>', 'search_user', clients.get_user, ['get'])

# Channels endpoints
flask_app.add_endpoint('/channel', "new_channel", channels.add_channel, ['post'])
flask_app.add_endpoint('/channels/<user>', "list_channels", channels.list_channels, ['get'])
flask_app.add_endpoint('/channel/<channel>/<user>', "remove_channel", channels.remove_channel, ['delete'])

# Queue endpoints
flask_app.add_endpoint('/channel/add', "new_queue", channels.add_queue, ['post'])
flask_app.add_endpoint('/channel/list/<channel>/<user>', "list_queues", channels.list_queue, ['get'])
flask_app.add_endpoint('/channel/remove/<channel>/<user>', 'remove_queue', channels.delete_queue, ['delete'])


@app.route('/')
def main():
    return "Administrator running"


if __name__ == "__main__":
    logging.info("Connecting to broker")
    syncker.connect()
    syncker.start_watcher()

    flask_app.run()