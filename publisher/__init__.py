import socket
import json

from jwt_controller import SecurityCell


if __name__ == '__main__':
    securityCell = SecurityCell().__get_instance__
    userKey = {'k': "lbMpr6VbKtDKtTYWYbtEaYIgTRo6MnyxPnNPquJ5mLY", 'kty': 'oct'}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('34.192.83.53', 5050))
        data = {
            "type": "connection",
            "from": socket.gethostname(),
            "user": "a11235de4ef7c79179a4f49aa2dd32cf",
            "topic": ""
        }
        s.sendall(json.dumps(data).encode())
        data = s.recv(4096)
        data = data.decode()
        data = securityCell.verify_token(data, userKey)

        if data['response'] == "welcome":
            while True:
                message = input("Message to send: ")
                data = {
                    "type": "message",
                    "from": socket.gethostname(),
                    "user": "a11235de4ef7c79179a4f49aa2dd32cf",
                    "topic": "Panditas",
                    "message": message
                }

                data = securityCell.generate_token(data, userKey['k'])

                try:
                    s.sendall(data.encode())
                except:
                    s.connect(('0.0.0.0', 5050))
                    s.sendall(message.encode())

                data = s.recv(4096)
                print(data.decode())

            print("All done")
        else:
            print("Error")