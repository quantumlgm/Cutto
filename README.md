<div align="center">

<h1>✂️ Cutto</h1>

**Self-hosted сервис для сокращения URL-адресов и генерации кастомных QR-кодов**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Docker](https://img.shields.io/badge/DevOps-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

<p align="center">
    Контейнеризированное приложение с гибридным кешированием, автоматическим контролем времени жизни ссылок и динамической аналитикой кликов.
</p>

<h4>
    <a href="#-особенности">Особенности</a> •
    <a href="#-стек-технологий">Стек</a> •
    <a href="#-структура-проекта">Структура</a> •
    <a href="#-быстрый-старт">Быстрый старт</a> •
    <a href="#-контакты">Контакты</a>
</h4>

</div>

---

## Особенности
* Умное сокращение URL: Генерация случайных безопасных слагов (`secrets.token_urlsafe`) или использование кастомных текстовых алиасов для коротких ссылок
* Кастомный движок QR-кодов: Создание qr-кодов с разными стилями: градиентная заливка, радиальное смешивание цветов, кастомизация формы модулей и глаз qr-кода
* TTL: Создание временных ссылок с указанием времени жизни в часах. Задачи на удаление регистрируются индивидуально через `APScheduler`, а также раз в 5 минут отрабатывает фоновый очиститель устаревших ссылок.
* Кеширование: Кеширование запросов в Redis на 1 час. При попадании в кеш счетчик кликов атомарно увеличивается, а изменения асинхронно синхронизируются с `PostgreSQL`. При промахе (`Cache Miss`) данные поднимаются из базы и пишутся в `Redis` через транзакционный пайплайн
* Аутентификация: Регистрация пользователей и аутентификация на основе JWT с контролем времени жизни токена. Ограничение доступа к административным эндпоинтам с помощью проверок ролей

## 🛠 Стек технологий
* Бэкенд:Python 3.12.10, FastAPI
* База данных и ORM: PostgreSQL, SQLAlchemy 2.0
* Кеширование: Redis 
* Планировщик задач: APScheduler 
* Безопасность: JWT (`pyjwt`), Passlib (`Bcrypt`), OAuth2 Bearer Tokens (`OAuth2PasswordBearer`)
* Фронтенд: React, TypeScript, Vite, CSS
* Документация API: Scalar, Docs, Swagger

Все использованные библиотеки вы можете посмотреть:
*  [pip (requirements.txt)](./requirements.txt)
*  [npm (package.json)](./frontend/package.json)

## С чего начать

### 1. Установка
```bash
git clone https://github.com/quantumlgm/Cutto.git
cd cutto
```

### 2. Настройка окружения
Создайте файл .env корне ./Cutto/app:

```env
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASS=your_secure_password
DB_NAME=cutto
```

### 3. Подключение к Redis
```bash
REDIS_HOST=redis
REDIS_PORT=6379
```

### 4. Безопасность JWT
Выполните в теминале
```bash
python -c "import secrets; print(secrets.token_hex(64))"
```
Затем
```
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
TOKEN_EXPERATION=30
```

### 5. Разрешенные адреса CORS
```bash
ALLOW_ORIGINS=["http://localhost:3000", "http://127.0.0.1:5173", "http://localhost:5173"]
```

### 6. Create tables:
```bash
alembic upgrade head
```
или если вы в docker
```bash
docker-compose exec app alembic upgrade head
```

### 7. Развертывание
```bash
docker compose up -d --build
```
Интерфейс фронтенда: http://localhost:5173

Документация Scalar: http://localhost:8000/

## Контакты

Баг-трекер: GitHub Issues

Телеграм : @quantumlgm
