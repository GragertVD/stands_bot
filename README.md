# VK Teams Bot + N8N Integration

Система VK Teams бота с интеграцией N8N для автоматизации процессов и SSL-защищенным доступом через Nginx.

## 🏗️ Архитектура

Система состоит из 4 сервисов:

- **Python API** (FastAPI) - VK Teams бот + HTTP API для интеграций
- **N8N** - Платформа для автоматизации и создания workflows  
- **Nginx** - Реверс-прокси с SSL поддержкой
- **Redis** - Кэширование и обмен данными между сервисами

## 🚀 Быстрый старт

### 1. Создание бота в VK Teams

1. Найдите бота `@Metabot` в VK Teams
2. Отправьте команду `/newbot` 
3. Следуйте инструкциям для создания бота
4. Получите токен бота (Bot Token)

### 2. Настройка и запуск

```bash
# Клонируем проект
git clone <repository-url> vk-teams-bot-system
cd vk-teams-bot-system

# Настраиваем проект 
make setup

# ВАЖНО: Редактируем .env файл - укажите токен бота!
nano .env

# Запускаем все сервисы
make up
```

### 3. Проверка работы

После запуска система будет доступна:

- **API документация**: http://localhost/docs
- **N8N интерфейс**: http://localhost/n8n/
  - Логин: `admin`
  - Пароль: `password123`
- **API health check**: http://localhost/health
- **Активные чаты**: http://localhost/chats

## ⚙️ Конфигурация

Отредактируйте файл `.env`:

```bash
# VK Teams Bot
VK_TEAMS_BOT_TOKEN=your_bot_token_here
VK_TEAMS_API_URL=https://api.internal.myteam.mail.ru/bot/v1

# N8N интеграция (URL webhook для отправки событий в N8N)
N8N_WEBHOOK_URL=http://n8n:5678/webhook/vk-teams

# Server settings
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
POLL_TIME=30

# Redis
REDIS_URL=redis://redis:6379
REDIS_DB=0

# Environment
ENVIRONMENT=development
DEBUG=true
```

**ВАЖНО**: Обязательно замените `your_bot_token_here` на реальный токен вашего бота!

## 📋 Команды управления

```bash
# Основные команды
make help           # Показать все доступные команды
make setup          # Первоначальная настройка
make build          # Собрать Docker образы
make up             # Запустить все сервисы
make down           # Остановить все сервисы
make restart        # Перезапустить все сервисы
make status         # Статус всех контейнеров
make clean          # Удалить все контейнеры и образы

# Логи
make logs           # Все сервисы
make logs-python    # Только Python приложение
make logs-n8n       # Только N8N
make logs-nginx     # Только Nginx

# Доступ к контейнерам
make shell-python   # Войти в контейнер Python приложения
make shell-n8n      # Войти в контейнер N8N
```

## 🤖 Функциональность бота

После запуска отправьте боту:

- `/start` - Приветственное сообщение и информация о возможностях
- `/help` - Справка по командам
- `/status` - Статус бота и всех интеграций
- **Любое сообщение** - Получите эхо-ответ + событие отправится в N8N

## 🔄 Интеграция с N8N

### Исходящие события (VK Teams → N8N)

Все сообщения пользователей автоматически отправляются в N8N по URL из `N8N_WEBHOOK_URL`:

```json
{
  "timestamp": "2025-09-28T16:07:43.227355",
  "source": "vk_teams",
  "event_type": "new_message", 
  "data": {
    "text": "Текст сообщения пользователя",
    "chat_id": "user@vkteam.ru",
    "user_name": "Иван Иванов",
    "user_id": "i.ivanov@vkteam.ru",
    "timestamp": 1759073645,
    "msg_id": "7555163776530514318"
  }
}
```

### Входящие сообщения (N8N → VK Teams)

N8N может отправлять сообщения пользователям через API:

```bash
# POST http://localhost/api/webhook
curl -X POST http://localhost/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "user@vkteam.ru",
    "message": "Сообщение от N8N!",
    "message_type": "text"
  }'
```

### Создание N8N Workflow

1. Откройте http://localhost/n8n/
2. Войдите с логином `admin` и паролем `password123`
3. Создайте новый workflow:
   - **Webhook Trigger** для приема событий от VK Teams
   - **HTTP Request** для отправки ответов обратно в VK Teams

## 🌐 HTTP API

Система предоставляет REST API:

```bash
# Основная информация
GET http://localhost/

# Проверка здоровья всех компонентов
GET http://localhost/health

# Список активных чатов
GET http://localhost/chats

# Детальная статистика
GET http://localhost/api/stats

# Отправка сообщения от N8N (webhook)
POST http://localhost/api/webhook
```

## 🐳 Docker

### Структура сервисов

```yaml
# docker-compose.yml
services:
  python-app:    # VK Teams бот + FastAPI
    ports: []    # Доступен только через nginx
  
  n8n:           # N8N automation platform
    ports: []    # Доступен через nginx по пути /n8n/
  
  nginx:         # Реверс-прокси 
    ports:
      - "80:80"   # HTTP
      - "443:443" # HTTPS (для продакшена)
  
  redis:         # Кэш и обмен данными
    ports: []    # Только для внутренних сервисов
```

### Ручное управление Docker

```bash
# Запуск
docker-compose up -d

# Остановка  
docker-compose down

# Логи конкретного сервиса
docker-compose logs -f python-app
docker-compose logs -f n8n
docker-compose logs -f nginx

# Перезапуск конкретного сервиса
docker-compose restart python-app
```

## 🚀 Развертывание в продакшене

### Продакшен информация
- **Домен**: gragert.ru
- **IP**: 93.115.203.7
- **Протокол**: HTTPS (обязательно)

### Быстрое развертывание

```bash
# На продакшен сервере
git clone <repository-url> vk-teams-bot-system
cd vk-teams-bot-system

# Размещаем SSL сертификаты
cp /path/to/fullchain.pem nginx/ssl/
cp /path/to/privkey.pem nginx/ssl/

# Настраиваем продакшн конфигурацию
cp production.env .env
nano .env  # Обязательно укажите токен бота!

# Запускаем продакшен
make prod-build
make prod-up
```

### Управление продакшеном

```bash
make prod-status    # Статус контейнеров
make prod-logs      # Просмотр логов
make prod-restart   # Перезапуск всех сервисов
make prod-down      # Остановка
```

### Доступные адреса в продакшене

- **Основной сайт**: https://gragert.ru/
- **API документация**: https://gragert.ru/docs
- **N8N интерфейс**: https://gragert.ru/n8n/
- **Health check**: https://gragert.ru/health

## 🔧 Разработка

### Структура проекта

```
vk-teams-bot-system/
├── python-app/              # Python приложение
│   ├── app/
│   │   ├── __init__.py      
│   │   ├── __main__.py      # Точка входа
│   │   ├── main.py          # Координатор системы
│   │   ├── bot.py           # VK Teams Bot логика
│   │   ├── api_server.py    # FastAPI сервер
│   │   ├── webhook_handler.py # N8N интеграция
│   │   └── config.py        # Конфигурация
│   ├── Dockerfile
│   └── requirements.txt
├── nginx/                   # Nginx конфигурация
│   ├── conf.d/
│   │   ├── default.conf     # Локальная разработка
│   │   └── production.conf  # Продакшен с SSL
│   └── ssl/                 # SSL сертификаты
├── n8n/
│   └── data/                # N8N данные (автоматически создается)
├── docker-compose.yml       # Разработка
├── docker-compose.production.yml # Продакшен
├── .env.example             # Пример настроек
├── production.env           # Продакшен настройки
├── Makefile                 # Команды управления
└── README.md               # Эта документация
```

### Добавление новой функциональности

1. **VK Teams бот**: Редактируйте `python-app/app/bot.py`
2. **API эндпоинты**: Добавьте в `python-app/app/api_server.py` 
3. **N8N интеграция**: Модифицируйте `python-app/app/webhook_handler.py`
4. **N8N Workflows**: Создавайте через веб-интерфейс http://localhost/n8n/

## 🛠️ Устранение неполадок

### Сервисы не запускаются

```bash
# Проверяем логи
make logs

# Проверяем статус
make status

# Пересобираем все с нуля
make clean
make build
make up
```

### Бот не отвечает

1. Проверьте токен в `.env`
2. Убедитесь что бот добавлен в контакты пользователя
3. Проверьте логи Python приложения: `make logs-python`

### N8N недоступен

1. Проверьте что порт 80 свободен
2. Проверьте Nginx логи: `make logs-nginx`
3. Убедитесь что все контейнеры запущены: `make status`

### Проблемы с SSL в продакшене

1. Проверьте права на сертификаты: `chmod 600 nginx/ssl/*.pem`
2. Убедитесь что сертификаты не истекли
3. Проверьте DNS записи для домена

## 📊 Мониторинг

### Health Check эндпоинты

```bash
# Проверка всей системы
curl http://localhost/health

# Детальная статистика  
curl http://localhost/api/stats

# Nginx health
curl http://localhost/nginx-health
```

### Логи и метрики

- Все логи автоматически ротируются (max 10MB на файл, 3 файла)
- Метрики доступны через `/api/stats`
- N8N имеет встроенный мониторинг выполнения workflows

## 🔒 Безопасность

- Никогда не публикуйте токен бота
- В продакшене обязательно используйте HTTPS
- Смените пароли N8N и Redis в `production.env`  
- Настройте файрвол на сервере
- Регулярно обновляйте Docker образы

## 📝 Лицензия

Проект создан для демонстрационных целей.