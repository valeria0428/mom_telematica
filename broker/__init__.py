from socket_controller import SocketController


if __name__ == '__main__':
    _socket = SocketController()
    _socket.configure('0.0.0.0', 5050)
    _socket.start_socket()