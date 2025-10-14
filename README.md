# hr_service

### Технологии

- Python 3.10+
- Django + Django REST Framework
- Poetry 
- PostgreSQL

### Установка и запуск

Открываем терминал, создаём папку, в которой будет располагаться проект и переходим в неё:
```bash
mkdir /ваш/путь
cd /ваш/путь
```
Клонируем репозотирий в эту папку, переходим в папку проекта:
```bash 
git clone https://github.com/DmitriyChubarov/hr_service.git
cd hr_system
```
Создаём .env файл
```bash
DEBUG=1
DB_NAME=hr_system_db
DB_USER=user
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```

Запускаем Docker на устройстве, после чего запускаем сервис:
```bash
docker compose up --build
```

Создание аккаунта суперюзера для HR:

```bash
docker compose run --rm web python3 manage.py createsuperuser
```

Для авторизации HR в django admin/Браузере:
```bash
http://localhost:8000/admin/

http://localhost:8000/api/auth/login/
```

Для запуска тестов:
```bash
docker compose run --rm web python3 manage.py test
```

Импорт файла(файл можно взять тут - https://disk.yandex.ru/d/uXWngywPCIJ6WQ):
```bash
http://localhost:8000/api/workers/import/
```
  
### Контакты
- tg: @eeezz_z
- gh: https://github.com/DmitriyChubarov

