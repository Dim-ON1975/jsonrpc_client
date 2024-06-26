import unittest
from unittest.mock import MagicMock, patch
from django.http import HttpRequest
from httpclient.jsonrpc_client import call_remote_method
from httpclient.views import CallAPIView
from httpclient.utils import create_temp_file, str_in_list_of_int


class TestCallRemoteMethod(unittest.TestCase):
    """
    Класс для тестирования функции call_remote_method,
    предназначенной для вызова удаленного метода API.
    """

    @patch('http.client.HTTPSConnection')  # Имитация HTTP-соединения и ответов от сервера
    def test_call_remote_method_success(self, mock_https_connection):
        """
        Тест успешного вызова удаленного метода.
        """
        # Создаём поддельный объект mock_response, имитирующий ответ от сервера.
        mock_response = MagicMock()

        # Настраиваем для возвращения определенных данных при вызове метода read
        mock_response.read.return_value = b'{"result": "Success"}'

        # Заменяем объект http.client.HTTPSConnection при помощи mock_https_connection
        mock_https_connection.return_value.getresponse.return_value = mock_response

        # Фактический результат тестового запроса
        result = call_remote_method("test_method", "test_params")

        # Ожидаемый результат
        expected_result = {
            "result": '{"result": "Success"}',
            "method_name": "test_method",
            "params": []
        }

        # Сравнение фактического и ожидаемого результатов
        self.assertEqual(result, expected_result)

    @patch('http.client.HTTPSConnection')
    def test_call_remote_method_error(self, mock_https_connection):
        """
        Тест обработки ошибки "Method not found".
        """
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"error": {"message": "Method not found"}}'
        mock_https_connection.return_value.getresponse.return_value = mock_response
        result = call_remote_method("nonexistent_method", "test_params")
        expected_result = {
            'result': "Не найден метод - {'error': {'message': 'Method not found'}}",
        }
        self.assertEqual(result, expected_result)

    @patch('http.client.HTTPSConnection')
    def test_call_remote_method_connection_error(self, mock_https_connection):
        """
        Тест обработки ошибки подключения к серверу.
        """
        # Устанавливаем "эффект", который должен быть вызван при вызове объекта mock_https_connection,
        # т.е. в данном случае возбуждение исключения типа Exception.
        mock_https_connection.side_effect = Exception("Connection error")
        result = call_remote_method("test_method", "test_params")
        expected_result = {
            "result": 'Ошибка подключения к серверу: Connection error'
        }
        self.assertEqual(result, expected_result)


class TestCallAPIView(unittest.TestCase):
    """ Класс для тестирования представления """

    @patch('httpclient.views.call_remote_method')
    def test_post_method_call_remote_method(self, mock_call_remote_method):
        # Создаем экземпляр класса CallAPIView
        view = CallAPIView()

        # Инициализируем атрибут request
        view.request = HttpRequest()
        view.request.method = 'POST'
        view.request.POST['method_name'] = 'test_method'
        view.request.POST['params'] = 'test_params'

        # Мокаем результат вызова удаленного метода
        mock_call_remote_method.return_value = {'result': 'Success'}

        # Вызываем метод post с имитированным запросом
        response = view.post(view.request)

        # Рендерим ответ
        response.render()

        # Проверяем, что результат вызова удаленного метода был возвращен и отображен на странице
        self.assertIn('Success', response.content.decode())


class TestFunctions(unittest.TestCase):
    """Класс тестирования функций из utils.py"""

    def test_create_temp_file(self):
        # Тестирование создания временного файла
        content = "This is a test content"
        file_path = create_temp_file(content)
        with open(file_path, 'r') as file:
            file_content = file.read()
        self.assertEqual(file_content, content)

    def test_str_in_list_of_int(self):
        # Тестирование преобразования строки с числами в список целых чисел
        params_1 = "1,2,3,4,5"
        result_1 = str_in_list_of_int(params_1)
        self.assertEqual(result_1, [1, 2, 3, 4, 5])

        # Тестирование преобразования строки без чисел в пустой список
        params_2 = "abc,def,ghi"
        result_2 = str_in_list_of_int(params_2)
        self.assertEqual(result_2, [])

        # Тестирование преобразования строки с пробелами и символами в список целых чисел
        params_3 = "1, 2, 3, abc, 4, def, 5"
        result_3 = str_in_list_of_int(params_3)
        self.assertEqual(result_3, [1, 2, 3, 4, 5])
