import socket
import json

from jwt_controller import SecurityCell


if __name__ == '__main__':
    securityCell = SecurityCell().__get_instance__
    userKey = {'k': "Byu502cUBiIFn_MtACnr69s9pbnqRT2WacuL28xUejc", 'kty': 'oct'}

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('34.192.83.53', 5050))
        print("Connected")
        data = {
            "type": "connection",
            "from": socket.gethostname(),
            "user": "3d63339eeb222943dc3161f114dcd4d7",
            "topic": ""
        }
        s.sendall(json.dumps(data).encode())
        data = s.recv(4096)
        data = data.decode()
        data = securityCell.verify_token(data, userKey)

        if data['response'] == "welcome":
            data = {
                "type": "subscribe",
                "from": socket.gethostname(),
                "user": "3d63339eeb222943dc3161f114dcd4d7",
                "topic": "Eventos"
            }

            data = securityCell.generate_token(data, userKey['k'])

            try:
                s.sendall(data.encode())
            except:
                s.connect(('0.0.0.0', 5050))

            data = s.recv(4096)
            print(data)

            while True:
                data = s.recv(4096)
                data = securityCell.verify_token(data.decode(), userKey)
                print(data)
        else:
            print("Error")
