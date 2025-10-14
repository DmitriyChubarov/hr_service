from rest_framework.test import APITestCase
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .models import Worker
import tempfile
import os
from openpyxl import Workbook

from .models import Worker

class BaseWorkerCase(APITestCase):
    """Базовый класс для тестов работников."""

    def setUp(self) -> None:
        """Настройка тестовых данных."""
        self.user = get_user_model().objects.create_user(
            username = 'admin',
            password = 'password'
        )

        Worker.objects.create(
            first_name = 'Сергей',
            middle_name = 'Сергееевич',
            last_name = 'Сергеев',
            email = 'sergei@mail.ru',
            position = 'dev',
            is_active = True,
            created_by = self.user
        )

class TestCreateWorkerCase(BaseWorkerCase):
    """Тесты для создания работников."""

    def base_worker(self, first_name: str, middle_name: str, last_name: str, email: str, position: str, is_active: bool) -> Response:
        """Базовый метод для создания работника."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/workers/', {
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'email': email,
            'position': position,
            'is_active': is_active,
            'created_by': self.user
        })
        return response
    
    def test_worker_create_not_auth(self) -> None:
        """Тест создания работника без авторизации."""
        response = self.client.post('/api/workers/', {
            'first_name': 'Сергей',
            'middle_name': 'Сергееевич',
            'last_name': 'Сергеев',
            'email': 'sergei@mail.ru',
            'position': 'dev',
            'is_active': True
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    def test_worker_create(self) -> None:
        """Тест успешного создания работника."""
        response = self.base_worker('Егор', 'Егорович', 'Егоров', 'egor@mail.ru', 'qa', True)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Worker.objects.count(), 2)

    def test_worker_create_with_empty_fields(self) -> None:
        """Тест создания работника с пустыми полями."""
        response = self.base_worker('', '', '', '', '', True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['first_name'][0], "This field may not be blank.")
        self.assertEqual(response.data['last_name'][0], "This field may not be blank.")
        self.assertEqual(response.data['email'][0], "This field may not be blank.")
        self.assertEqual(response.data['position'][0], "This field may not be blank.")

    def test_worker_create_with_email_already_exists(self) -> None:
        """Тест создания работника с существующим email."""
        response = self.base_worker('Егор', 'Егорович', 'Егоров', 'sergei@mail.ru', 'qa', True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0], "worker with this email already exists.")

    def test_worker_create_with_invalid_email(self) -> None:
        """Тест создания работника с невалидным email."""
        response = self.base_worker('Егор', 'Егорович', 'Егоров', 'sergei', 'qa', True)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['email'][0], "Enter a valid email address.")

class TestGetWorkerCase(BaseWorkerCase):    
    """Тесты для получения работников."""
    def base_workers_get(self, p_f) -> Response:
        """Базовый метод для получения списка работников."""
        response = self.client.get(f'/api/workers/{p_f}')
        return response

    def test_workers_get(self) -> None:
        """Тест получения списка работников."""
        response = self.base_workers_get('')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['first_name'], 'Сергей')

    def test_workers_get_with_fil(self) -> None:
        """Тест получения работников с фильтрацией."""
        response = self.base_workers_get('?is_active=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_workers_get_with_pag(self) -> None:
        """Тест получения работников с пагинацией."""
        response = self.base_workers_get('?is_active=true')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['next'], None)

    def base_worker_get(self, pk) -> Response:
        """Базовый метод для получения одного работника."""
        response = self.client.get(f'/api/workers/{pk}/')
        return response

    def test_worker_get(self) -> None:
        """Тест получения одного работника."""
        worker = Worker.objects.first()
        response = self.base_worker_get(worker.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Сергей')

    def test_worker_get_with_invalid_pk(self) -> None:
        """Тест получения работника с несуществующим ID."""
        response = self.base_worker_get(100)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], "Сотрудника с id=100 не существует.")

    def test_worker_get_with_str_pk(self) -> None:
        """Тест получения работника со строковым ID."""
        response = self.base_worker_get('abc')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], "Некорректный идентификатор")
        
class TestUpdateWorkerCase(BaseWorkerCase):
    """Тесты для обновления работников."""

    def base_worker_update(self, pk, data) -> Response:
        """Базовый метод для обновления работника."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/workers/{pk}/', data)
        return response
    
    def test_worker_update_success(self) -> None:
        """Тест успешного обновления работника."""
        worker = Worker.objects.first()
        response = self.base_worker_update(worker.id, {
            'first_name': 'НовоеИмя',
            'position': 'НоваяДолжность'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'НовоеИмя')
        self.assertEqual(response.data['position'], 'НоваяДолжность')
    
    def test_worker_update_not_found(self) -> None:
        """Тест обновления несуществующего работника."""
        response = self.base_worker_update(999, {
            'first_name': 'НовоеИмя'
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], "Сотрудника с id=999 не существует.")
    
    def test_worker_update_unauthorized(self) -> None:
        """Тест обновления работника без авторизации."""
        worker = Worker.objects.first()
        response = self.client.patch(f'/api/workers/{worker.id}/', {
            'first_name': 'НовоеИмя'
        })
        self.assertEqual(response.status_code, 403)

class TestDeleteWorkerCase(BaseWorkerCase):
    """Тесты для удаления работников."""

    def base_worker_delete(self, pk) -> Response:
        """Базовый метод для удаления работника."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/workers/{pk}/')
        return response
    
    def test_worker_delete_success(self) -> None:
        """Тест успешного удаления работника."""
        worker = Worker.objects.first()
        initial_count = Worker.objects.count()
        
        response = self.base_worker_delete(worker.id)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Worker.objects.count(), initial_count - 1)
    
    def test_worker_delete_not_found(self) -> None:
        """Тест удаления несуществующего работника."""
        response = self.base_worker_delete(999)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], "Сотрудника с id=999 не существует.")
    
    def test_worker_delete_unauthorized(self) -> None:
        """Тест удаления работника без авторизации."""
        worker = Worker.objects.first()
        response = self.client.delete(f'/api/workers/{worker.id}/')
        self.assertEqual(response.status_code, 403)
    
    def test_worker_delete_invalid_id(self) -> None:
        """Тест удаления работника со строковым ID."""
        response = self.base_worker_delete('abc')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'Некорректный идентификатор')


"""Надо добавить тесты на import"""