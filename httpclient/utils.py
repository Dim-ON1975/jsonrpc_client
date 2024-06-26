import re
import tempfile


def create_temp_file(content: str) -> str:
    """
    Создает временный файл в памяти и записывает в него содержимое.
    Возвращает путь к созданному временному файлу.

    :param content: Строковое (многострочное) значение, которое нужно сохранить во временном файле, str.
    :return: Имя временного файла, str.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(content.encode('utf-8'))
    temp_file.close()
    return temp_file.name


def str_in_list_of_int(params: str) -> list:
    """
    Преобразует строку, содержащую набор различных символов, включая целые числа,
    в список из целых чисел. Если в строке нет целых чисел, то возвращает пустой список.

    :param params: Строка, содержащая набор различных символов, str.
    :return: Список целых чисел или пустой список, list.
    """

    # Удаляем все пробелы из params
    params = re.sub(r"\s+", "", params, flags=re.UNICODE)
    # Заменяем все символы, не являющиеся цифрами на запятые
    params = re.sub(r'\D', ',', params)
    # Удаляем дубликаты запятых в строке
    params = re.sub(r',+', ',', params)
    # Удаляем запятые в начале и в конце строки
    params = re.sub(r'^,|,$', '', params)

    # Преобразуем params в список целых чисел по разделителю "запятая"
    params_list = [int(x) if x else 0 for x in params.split(',')]
    if len(params_list) == 1 and params_list[0] == 0:
        params_list = []

    return params_list
