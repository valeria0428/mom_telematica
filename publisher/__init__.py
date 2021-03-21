import socket
import json


if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('0.0.0.0', 5050))
        data = {
            "type": "connection",
            "from": socket.gethostname(),
            "user": "a11235de4ef7c79179a4f49aa2dd32cf",
            "topic": ""
        }
        s.sendall(json.dumps(data).encode())
        data = s.recv(4096)
        data = data.decode()
        print(data)
        if data == "welcome":
            while True:
                message = input("Message to send: ")
                try:
                    s.sendall(message.encode())
                except:
                    s.connect(('0.0.0.0', 5050))
                    s.sendall(message.encode())

                data = s.recv(4096)
                print(data.decode())

            print("All done")
        else:
            print("Error")