import http.client
import json
import tempfile
from django.conf import settings
from urllib.parse import urlparse
import re


def create_temp_file(content):
    """
    Создает временный файл в памяти и записывает в него содержимое.
    Возвращает путь к созданному временному файлу.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(content.encode('utf-8'))
    temp_file.close()
    return temp_file.name


def call_remote_method(method_name: str, params: str) -> dict:
    """
    Функция для вызова удаленного метода API.
    Возвращает данные, полученные в ответе от сервера.

    :param method_name: Передаваемый метод, str
    :param params: Передаваемые параметры, str
    :return: Словарь, содержащий данные об ответе сервера, метод и параметры, dict.
    """

    # Получаем содержимое сертификата, ключа и эндпоинт из настроек Django
    # Создание временных файлов из содержимого сертификата и ключа
    certificate_file = create_temp_file(settings.CERTIFICATE_CONTENT)
    private_key_file = create_temp_file(settings.PRIVATE_KEY_CONTENT)

    # Разбор URL на его составные части: схема, netloc, путь, параметры, запрос, фрагмент.
    # ParseResult(scheme='https', netloc='slb.medv.ru', path='/api/v2/', params='', query='', fragment='')
    parsed_url = urlparse(settings.ENDPOINT)
    endpoint = parsed_url.netloc
    path = parsed_url.path

    conn = http.client.HTTPSConnection(endpoint, key_file=private_key_file, cert_file=certificate_file)

    # Подготовка данных для jsonrpc-запроса

    # Удаляем все пробелы из params
    params = re.sub(r"\s+", "", params, flags=re.UNICODE)
    # Заменяем все символы, не являющиеся цифрами на запятые
    params = re.sub(r'\D', ',', params)
    # Удаляем дубликаты запятых в строке
    params = re.sub(r',+', ',', params)
    # Удаляем запятые в начале и в конце строки
    params = re.sub(r'^,|,$', '', params)

    # Преобразуем params в список по разделителю "запятая"
    params_list = params.split(',')
    if len(params_list) == 1 and params_list[0] == '':
        params_list = []

    payload = {
        "jsonrpc": "2.0",
        "method": method_name,
        "params": params_list,
        "id": 1
    }
    headers = {'Content-Type': 'application/json'}

    # Подключение к endpoint и обработка ошибок
    # Отправка jsonrpc-запроса на сервер
    conn.request("POST", path, body=json.dumps(payload), headers=headers)

    # Получение ответа от сервера
    response = conn.getresponse()
    data = response.read().decode()
    conn.close()

    return {
        "result": data,
        "method_name": method_name,
        "params": params_list
    }
