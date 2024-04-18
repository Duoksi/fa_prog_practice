import socket
import json
import struct


def receive_with_size(socket):
    data_size = socket.recv(struct.calcsize('P'))
    if not data_size:
        return None
    data_size = struct.unpack('!I', data_size)[0]
    data = b""
    while len(data) < data_size:
        if data_size - len(data) < 1024:
            packet = socket.recv(data_size - len(data))
            data += packet
            return data
        packet = socket.recv(1024)
        if not packet:
            return None
        data += packet
    return data

def main():
    server_address = ('localhost', 65432)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    while True:
        command = input("Введите команду (get_info / set_dir <путь> / save_dump / exit): ")
        client_socket.send(command.encode())

        if command == 'exit':
            break
        elif command == 'get_info':
            data = receive_with_size(client_socket)
            if data:
                files_info = json.loads(data.decode())
                print("Информация о файлах:")
                for file_info in files_info:
                    print(file_info)
            else:
                print("Ошибка при получении данных")
        elif command.startswith('set_dir'):
            response = client_socket.recv(1024).decode()
            print(response)
        elif command.startswith('save_dump'):
            response = client_socket.recv(1024).decode()
            print(response)
        else:
            print("Введите команду правильно!")
            continue

    client_socket.close()

if __name__ == "__main__":
    main()
