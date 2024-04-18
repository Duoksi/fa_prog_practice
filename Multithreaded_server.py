import os
import json
import socket
import struct
import threading
import psutil
import xml.etree.ElementTree as ET
import time

class Node:

    def __init__(self, value):
        self.value = value
        self.left = self.right = None

class Tree:

    def __init__(self):
        self.root = None

    def insert_node(self, node, value):
        if node is None:
            return Node(value)

        if value < node.value:
            node.left = self.insert_node(node.left, value)
        else:
            node.right = self.insert_node(node.right, value)
        return node

    def save_tree_json(self, filename):
        def serialize(node):
            if node is None:
                return None
            return {
                'value': node.value,
                'left': serialize(node.left),
                'right': serialize(node.right)
            }

        serialized_tree = serialize(self.root)
        with open(filename, 'w') as file:
            json.dump(serialized_tree, file, indent=4)

    def save_tree_xml(self, filename):
        def serialize(node, parent):
            if node is None:
                return
            element = ET.SubElement(parent, 'node')
            ET.SubElement(element, 'value').text = str(node.value)
            serialize(node.left, element)
            serialize(node.right, element)

        root_element = ET.Element('root')
        serialize(self.root, root_element)
        tree = ET.ElementTree(root_element)
        tree.write(filename)

def create_directory():
    current_time = time.strftime("%d-%m-%Y_%H-%M-%S")
    directory_name = os.path.join(os.getcwd(), current_time)
    os.makedirs(directory_name)
    return directory_name

def read_json_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def get_processes():
    """ Получение информации о процессах. """
    processes_info = []
    try:
        output = os.popen('tasklist /FO CSV').read().strip().split('\n')
        for line in output[1:]:
            parts = line.strip().split('","')
            pid = int(parts[1])
            name = parts[0].strip('"')
            cmdline = parts[-1].strip('"')
            process_info = {
                'pid': pid,
                'name': name,
                'cmdline': cmdline,
            }
            processes_info.append(process_info)
    except Exception as e:
        print("Error:", e)
    return processes_info

def get_processes_info():
    processes = []
    for proc in psutil.process_iter():
        process_info = proc.as_dict(attrs=['pid', 'name', 'username'])
        processes.append(process_info)
    return processes

def send_data(conn, data):
    """ Отправка данных по сети. """
    conn.sendall(json.dumps(data).encode())
    
def get_file_info(path):
    """ Получение информации о файле в виде словаря. """
    file_stat = os.stat(path)
    return {
        'name': os.path.basename(path),
        'path': path,
        'size': file_stat.st_size,
        'modified': file_stat.st_mtime,
    }

def send_data_with_size(socket, data):
    data_size = struct.pack('!I', len(data))
    print(data_size)
    socket.sendall(data_size)
    socket.sendall(data)

def list_files_recursive(directory):
    """ Рекурсивный обход всех файлов и подпапок в указанной директории. """
    files_info = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            files_info.append(get_file_info(file_path))
    return files_info



def handle_client_connection(conn):
    """ Обработка подключения клиента. """
    while True:
        command = conn.recv(1024).decode()
        if not command:
            break
        if command == "update":
            processes_info = get_processes_info()
            data = json.dumps(processes_info).encode()
            send_data_with_size(conn, data)
        elif command == "get_info":
            current_directory = os.getcwd()
            files_info = list_files_recursive(current_directory)
            send_data_with_size(conn, json.dumps(files_info).encode())
        elif command.startswith('set_dir'):
            new_root_directory = command.split(' ', maxsplit=1)[1]
            os.chdir(new_root_directory)
            conn.send("Корневая директория изменена".encode())
        elif command == 'save_dump':
            current_directory = os.getcwd()
            files_info = list_files_recursive(current_directory)

            with open('file_dump.json', 'w', encoding='utf-8') as f:
                json.dump(files_info, f, indent=4, ensure_ascii=False)

            conn.send("Информация о файлах сохранена в file_dump.json в корневой директории".encode())
        elif command == 'create tree':
            print('Команда принята')
            t = Tree()
            directory = create_directory()
            file_counter = 1

            while True:
                data = conn.recv(1024)
                user_input = data.decode()
                print('Числе передано')
                if not data:
                    break

                if user_input.strip() == "":
                    if t.root is not None:
                        json_filename = os.path.join(directory, f"{file_counter}.json")
                        t.save_tree_json(json_filename)
                        t.save_tree_xml(os.path.join(directory, f"{file_counter}.xml"))

                        
                        json_data = read_json_file(json_filename)
                        json_data_str = json.dumps(json_data).encode()  
                        file_len = len(json_data_str)
                        print(f"Размер файла {json_filename}: {file_len} байт")

                        conn.send(struct.pack('!i', file_len) + json_data_str)

                        file_counter += 1
                        t.root = None
                        break
                else:
                    t.root = t.insert_node(t.root, user_input)


def main():
    HOST = '127.0.0.1'
    PORT = 65432

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(4)
    print('Сервер слушает ...')

    while True:
        conn, addr = server_socket.accept()
        print('Подключено к', addr)
        client_thread = threading.Thread(target=handle_client_connection, args=(conn,))
        client_thread.start()

if __name__ == "__main__":
    main()