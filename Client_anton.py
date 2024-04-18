import socket
import struct
import json
"""
Клиентская часть
"""
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 65432))
client_socket.send('create tree'.encode())
while True:
    user_input = input("Введите число для отправки на сервер (Enter для завершения): ")

    if user_input.strip() == "":
        client_socket.sendall(b" ")
        break
    else:
        client_socket.sendall(user_input.encode())

data = client_socket.recv(1024) 
if len(data) >= 4:
    file_len = struct.unpack('!i', data[:4])[0]
    json_data = data[4:]

    if len(json_data) >= file_len:
        json_str = json_data[:file_len].decode()
        data = json.loads(json_str)
        print("Полученные данные (формат json):")
        print(data)
    else:
        print("Получены неполные данные")
else:
    print("Длина данных меньше 4 байт. Не удается распаковать.")

