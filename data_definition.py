import requests
import json
from datetime import datetime
import os


from config import SERVERS, ARGS, JSON_PATH, STRING, JSON_ENABLE  # подтягиваем переменные из конфига


def get_haproxy_stats(url, statistic_data):
    """
    Функция для считывания данных с сервера HAProxy и записи в statistic_data
    :param url: строка подключения к HAProxy
    :param statistic_data: уже имеющиеся данные
    :return:
    """

    # запрос к серверу
    # try:
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         data_dict = response.json()
    #     else:
    #         print(f"Ошибка: Не удалось получить данные. Status code: {response.status_code}")
    #         return None
    # except requests.exceptions.RequestException as error:
    #     print(f"Ошибка: {error}")
    #     return None

    # Временная имитация запроса данных с сервера
    # TEST
    # data = input("Data: ")  # Для теста вводим данные с клавиатуры
    data = STRING
    data_dict = json.loads(data)

    # Обработка данных
    needed_data = extract_data(data_dict)

    # включаем запись в json, если включена настройка
    if JSON_ENABLE == 1:
        update_json_file(JSON_PATH, needed_data)

    # Обновление данных в памяти
    statistic_data = update_data_in_memory(statistic_data, needed_data)
    # Возвращаем изменённые данные
    return statistic_data


def extract_data(server_data):
    """
    Извлечение нужных данных из json
    :param server_data: json данные с сервера
    :return: словарь вида
            {
                "server1": {
                    "param1": value1,
                    "param2": value2
                },
                "server2": {
                    "param1": value1,
                    "param2": value2
                }
            }
    """
    data = {}  # данные, которые будем получать
    for row in server_data:  # бежим по строкам статы
        pxname = None
        svname = None
        for param in row:  # бежим по параметрам внутри строки
            # находим pxname и проверяем, есть ли он в нашем словаре
            if param['field']['name'] == "pxname":
                if param['value']['value'] in SERVERS.keys():
                    pxname = param['value']['value']  # если есть, записываем этот pxname (нужен для ключа)
                else:
                    break  # если нету, то прерываем цикл пробега по параметрам и пропускаем строку
            # находим svname и проверяем, есть ли он в нашем словаре по вышенайденному pxname
            if param['field']['name'] == "svname":
                if param['value']['value'] in SERVERS[pxname]:
                    svname = param['value']['value']  # если есть, записываем этот svname (нужен для данных)
                else:
                    break  # если нету, то прерываем цикл пробега по параметрам и пропускаем строку

            # если всё заебумба, записываем данные сервака
            server = f"{pxname[0:4]}_{svname}"

            # костыль, т.к. есть какие-то записи, где svname не находится и ставится None
            # + не перезаписываем данные, если уже есть такой ключ
            if (svname is not None) and (server not in data.keys()):
                data[server] = {}
            # если всё заебумба (т.е. строка нам подходит), то бежим дальше по параметрам и ищем нужные нам

            # если параметр есть в нашем списке
            if param['field']['name'] in ARGS.keys():
                # то добавляем данные в наш словарь

                arg = param['field']['name']
                data[server][arg] = int(param['value']['value'])

        else:
            continue  # если внутренний цикл остановлен break, то пропускаем строку

    # добавляем время считывания
    now_time = datetime.now()
    now_time = now_time.strftime("%H:%M:%S")
    data['time'] = {}
    data['time']['time'] = now_time

    return data


def update_json_file(file_path, data):
    """
    Занесение данных в json файл
    :param file_path: путь к файлу
    :param data: данные, которые нужно упаковать в json
    :return:
    """
    if os.path.exists(file_path):
        # Если файл уже существует, загружаем данные из него
        with open(file_path, 'r') as file:
            existing_data = json.load(file)

        # Обновляем данные из файла новыми данными
        for server, params in data.items():
            if server in existing_data:
                for param, value in params.items():
                    if param in existing_data[server]:
                        # Проверяем, является ли значение параметра списком
                        if isinstance(existing_data[server][param], list):
                            existing_data[server][param].append(value)
                        else:
                            # Если не является списком, создаем список из существующего значения
                            # и добавляем новое значение
                            existing_data[server][param] = [existing_data[server][param], value]
                    else:
                        # Если параметра нет, добавляем его со значением в виде списка
                        existing_data[server][param] = [value]
            else:
                # Если сервера нет, добавляем новый сервер с параметром и его значением в виде списка
                existing_data[server] = {param: [value] for param, value in params.items()}
        new_data = existing_data
    else:
        # Если файл не существует, создаем новый файл с данными
        new_data = data

    # Записываем данные в файл JSON
    with open(file_path, 'w') as file:
        json.dump(new_data, file, indent=4)


def update_data_in_memory(existing_data, data):
    """
    Обновление данных графиков в памяти
    :param existing_data: существующие данные в памяти
    :param data: новые данные, которые нужно добавить
    :return: обновленные данные в памяти
    """
    # TODO зачем?! Убери нафиг. Можно и без копи, просто бери основной словарь
    updated_data = existing_data.copy()

    # Обновляем данные из новых данных
    for server, params in data.items():
        if server in updated_data:
            for param, value in params.items():
                # Добавляем новые значения в существующие списки
                if isinstance(updated_data[server][param], list):
                    updated_data[server][param].append(value)
                else:
                    # Если значения не является списком, создаем новый список с существующим и добавляем новое значение
                    updated_data[server][param] = [updated_data[server][param], value]
        else:
            # Если сервера нет, добавляем новый сервер с параметром и его значением в виде списка
            updated_data[server] = {param: [value] for param, value in params.items()}

    return updated_data
