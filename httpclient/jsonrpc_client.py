import http.client
import json
from urllib.parse import urlparse
from config.settings import ENDPOINT, CERTIFICATE_CONTENT, PRIVATE_KEY_CONTENT
from httpclient.utils import create_temp_file, str_in_list_of_int


def call_remote_method(method_name: str, params: str) -> dict:
    """
    Функция для вызова удаленного метода API.
    Возвращает данные, полученные в ответе от сервера.

    :param method_name: Передаваемый метод, str
    :param params: Передаваемые параметры, str
    :return: Словарь, содержащий данные об ответе сервера, метод и параметры, dict.
    """

    # Подготовка данных для jsonrpc-запроса
    params_list = str_in_list_of_int(params)

    payload = {
        "jsonrpc": "2.0",
        "method": method_name,
        "params": params_list,
        "id": 1
    }
    headers = {'Content-Type': 'application/json'}

    # Получаем содержимое сертификата и ключа из настроек Django
    # Создание временных файлов из содержимого сертификата и ключа
    certificate_file = create_temp_file(CERTIFICATE_CONTENT)
    private_key_file = create_temp_file(PRIVATE_KEY_CONTENT)

    # Подключение endpoint и обработка ошибок
    try:
        conn = http.client.HTTPSConnection(urlparse(ENDPOINT).netloc,
                                           key_file=private_key_file,
                                           cert_file=certificate_file)

        # Отправка jsonrpc-запроса на сервер
        conn.request("POST",
                     urlparse(ENDPOINT).path,
                     body=json.dumps(payload),
                     headers=headers)

        # Получение ответа от сервера
        response = conn.getresponse()
        data = response.read().decode()
        conn.close()

        result = {
            "result": data,
            "method_name": method_name,
            "params": params_list
        }

        response_json = json.loads(data)
        if 'error' in response_json and response_json['error']['message'] == 'Method not found':
            data = 'Не найден метод - ' + str(response_json)
            result = {"result": data}

    except Exception as e:
        data = 'Ошибка подключения к серверу: ' + str(e)
        result = {"result": data}

    return result
