# Cutto - URL Shortening Service

Self-hosted service for shortening URLs and generating customizable QR codes. The project supports real-time click tracking with hybrid caching (Redis + PostgreSQL), a QR code editor for links, automatic link expiration by schedule, and custom slugs. Fully containerized using Docker.

## Features
* Smart URL shortening: Generation of random secure slugs (`secrets.token_urlsafe`) or use of custom text aliases for short links
* Custom QR code engine: Creation of QR codes with different styles: gradient fill, radial color blending, customization of module shapes and QR code eyes
* TTL: Creation of temporary links with specified lifetime in hours. Deletion tasks are registered individually via `APScheduler`, and a background cleaner of expired links runs every 5 minutes.
* Caching: Caching requests in Redis for 1 hour. On cache hit, click counter is atomically incremented, and changes are asynchronously synchronized with `PostgreSQL`. On cache miss, data is fetched from the database and written to Redis via transactional pipeline
* Authentication: User registration and authentication based on JWT with token lifetime control. Access restriction to admin endpoints using role checks

## 🛠 Tech Stack
* Backend: Python 3.12.10, FastAPI
* Database and ORM: PostgreSQL, SQLAlchemy 2.0
* Caching: Redis
* Task scheduler: APScheduler
* Security: JWT (`pyjwt`), Passlib (`Bcrypt`), OAuth2 Bearer Tokens (`OAuth2PasswordBearer`)
* Frontend: React, TypeScript, Vite, CSS
* API documentation: Scalar, Docs, Swagger

All used libraries can be viewed here:
* [pip (requirements.txt)](./requirements.txt)
* [npm (package.json)](./frontend/package.json)

## 📦 Architecture and Project Structure
[View (README.structure.md)](./README.structure.md)

## 🚀 Getting Started

### 1. Installation
```bash
git clone https://github.com/quantumlgm/Cutto.git
cd cutto
```

### 2. Environment Setup
Create .env in root ./Cutto/app:

```env
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASS=your_secure_password
DB_NAME=cutto
```

### 3. Redis Connection
```bash
REDIS_HOST=redis
REDIS_PORT=6379
```

### 4. JWT Security
Run in terminal
```bash
python -c "import secrets; print(secrets.token_hex(64))"
```
Then
```
SECRET_KEY=your_super_secret_jwt_key_here
ALGORITHM=HS256
TOKEN_EXPERATION=30
```

### 5. Allowed CORS Origins
```bash
ALLOW_ORIGINS=["http://localhost:3000", "http://127.0.0.1:5173", "http://localhost:5173"]
```

### 6. Create tables:
```bash
alembic upgrade head
```
or if you are using docker
```bash
docker-compose exec app alembic upgrade head
```

### 7. Deployment
```bash
docker compose up -d --build
```
Frontend interface: http://localhost:5173

Interactive API documentation (Scalar): http://localhost:8000/

## 🤝 Contacts

Bug tracker: GitHub Issues

Telegram: @quantumlgm

