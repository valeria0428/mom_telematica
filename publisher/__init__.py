import logging

from flask_instance import FlaskInstance
from socket_actions import SocketActions


logging.basicConfig(level=logging.DEBUG)  # Configure logging

# Configure flask
flask_app = FlaskInstance().__getinstance__
app = flask_app.get_app()

socket_action = SocketActions().__get_instance__

flask_app.add_endpoint('/message', 'message', socket_action.new_message, ['post'])
flask_app.add_endpoint('/disconnect', 'disconnect', socket_action.disconnect, ['post'])


@app.route('/')
def main():
    return "Running"


if __name__ == '__main__':
    try:
        socket_action.start_socket()
        flask_app.run()
    except Exception as err:
        logging.error(err)
