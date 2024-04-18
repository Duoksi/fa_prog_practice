import socket
import os
from datetime import datetime
import json
import struct

def receive_file(sock, file_path, size):
    data = ''
    while size > 0:
        buf = sock.recv(1024).decode()
        data += buf
        size -= 1024
    with open(file_path,'w') as f:
        json.dump(json.loads(data),f, indent=4)
    print('Файл записан')


def send_command(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall(b'update')
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
    os.makedirs(dt_string, exist_ok=True)
    size_data = sock.recv(4) 
    size = struct.unpack("!I", size_data)[0]
    print(f'Размер входящего файла {size}')
    receive_file(sock, f"{dt_string}/processes.json", size)
    sock.close()

if __name__ == "__main__":
    host = '127.0.0.1'
    port = 65432
    send_command(host, port)