import socket
import json
import datetime
import struct

def save_file(data):
    """ Сохранение данных в файл. """
    current_datetime = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")     # Получение текущей даты и времени в формате строки
    filename = f"{current_datetime}.json"                                        # Создание имени файла на основе даты и времени

    decode_data = data.decode()                                                  # Декодируем байтовые данные в строку

    with open(filename, 'w', encoding='utf-8') as json_file:                                       # Открытие файла для записи
        json.dump(json.loads(decode_data), json_file, indent=4, ensure_ascii=False)

def main():
    """ Основная функция клиента. """

    HOST = '127.0.0.1'                      # IP-адрес сервера
    PORT = 65432                            # Порт сервер

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:        # Создание сокета TCP
        s.connect((HOST, PORT))                                         # Подключение к серверу
        s.sendall("update".encode())                # Отправка команды на сервер в байтовом формате

        size_data = s.recv(4)                               # Получение байтов размера данных
        size = struct.unpack("!I", size_data)[0]            # Распаковка байтов размера данных в целое число

        data = b''                                          # Хранение принятых данных
        packet_size = 1024
        while len(data) < size:
            packet = s.recv(packet_size)               # Получение пакета данных
            if not packet:                                  # Если пакет данных пустой
                break                                       # Прерываем цикл
            data += packet                                 # Добавление принятых данных к общему объему данных

    if data:
        save_file(data)
        print("Файл успешно сохранен.")
    else:
        print("Не удалось получить данные от сервера.")

if __name__ == "__main__":
    main()
