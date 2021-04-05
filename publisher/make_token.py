import pyperclip

from jwt_controller import SecurityCell

jwt = SecurityCell().__get_instance__

user_key = input("Ingresa la llave del usuario: \n")

while True:
    print("\n_________________________________________________\n")
    message = input("Ingresa el mensaje que deseas enviar: ")
    topic = input("Ingresa el topico al que deseas enviar: ")

    claim = {"message": message, "topic": topic}
    key = jwt.generate_token(claim, user_key)
    print(key)
    pyperclip.copy(key)
    print("___________JWT token copiado en el portapapeles___________")


