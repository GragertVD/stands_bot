# Makefile для VK Teams Bot + N8N + Nginx

SHELL := /bin/sh

.PHONY: help build up down logs clean restart status setup
.PHONY: logs-python logs-n8n logs-nginx shell-python shell-n8n
.PHONY: prod-build prod-up prod-down prod-logs prod-restart prod-status

# Показать помощь
help:
	@echo "VK Teams Bot System - Команды управления:"
	@echo ""
	@echo "Основные команды (разработка):"
	@echo "  setup          - Первоначальная настройка проекта"
	@echo "  build          - Собрать Docker образы"
	@echo "  up             - Запустить все сервисы (Python + N8N + Nginx + Redis)"
	@echo "  down           - Остановить все сервисы"
	@echo "  restart        - Перезапустить все сервисы"
	@echo "  logs           - Показать логи всех сервисов"
	@echo "  status         - Показать статус всех контейнеров"
	@echo "  clean          - Удалить все контейнеры и образы"
	@echo ""
	@echo "Логи отдельных сервисов:"
	@echo "  logs-python    - Логи Python приложения"
	@echo "  logs-n8n       - Логи N8N"
	@echo "  logs-nginx     - Логи Nginx"
	@echo ""
	@echo "Доступ к контейнерам:"
	@echo "  shell-python   - Войти в контейнер Python приложения"
	@echo "  shell-n8n      - Войти в контейнер N8N"
	@echo ""
	@echo "Продакшн (gragert.ru):"
	@echo "  prod-build     - Собрать продакшен образы"
	@echo "  prod-up        - Запустить продакшен сервисы"
	@echo "  prod-down      - Остановить продакшен сервисы"
	@echo "  prod-restart   - Перезапустить продакшен сервисы"
	@echo "  prod-logs      - Логи продакшен сервисов"
	@echo "  prod-status    - Статус продакшен контейнеров"

# Первоначальная настройка
setup:
	@echo "🚀 Настройка VK Teams Bot System..."
	@if [ ! -f .env ]; then cp .env.example .env; echo "✅ Создан файл .env из примера"; fi
	@mkdir -p n8n/data nginx/ssl
	@echo "⚠️  ВАЖНО: Отредактируйте файл .env и укажите токен бота!"
	@echo "✅ Проект настроен! Теперь выполните 'make up'"

# Собрать образы
build:
	@echo "🔨 Сборка Docker образов..."
	docker-compose build --no-cache

# Запустить все сервисы
up:
	@echo "🚀 Запуск всех сервисов..."
	docker-compose up -d
	@echo "✅ Сервисы запущены!"
	@echo ""
	@echo "🌐 Доступные адреса:"
	@echo "  • API документация: http://localhost/docs"
	@echo "  • N8N интерфейс: http://localhost/n8n/"
	@echo "  • API health: http://localhost/health"
	@echo "  • Активные чаты: http://localhost/chats"
	@echo ""
	@echo "🔐 N8N логин: admin, пароль: password123"

# Остановить все сервисы
down:
	@echo "🛑 Остановка всех сервисов..."
	docker-compose down

# Перезапустить сервисы
restart: down up

# Логи всех сервисов
logs:
	docker-compose logs -f

# Логи отдельных сервисов
logs-python:
	docker-compose logs -f python-app

logs-n8n:
	docker-compose logs -f n8n

logs-nginx:
	docker-compose logs -f nginx

# Доступ к контейнерам
shell-python:
	docker-compose exec python-app sh

shell-n8n:
	docker-compose exec n8n sh

# Показать статус
status:
	@echo "📊 Статус всех контейнеров:"
	@docker-compose ps

# Очистка
clean:
	@echo "🧹 Удаление всех контейнеров и образов..."
	docker-compose down -v --rmi all
	docker system prune -f

# ================================
# ПРОДАКШН КОМАНДЫ
# ================================

# Собрать продакшен образы
prod-build:
	@echo "🔨 Сборка продакшен образов..."
	docker-compose -f docker-compose.production.yml build --no-cache

# Запустить продакшен сервисы
prod-up:
	@echo "🚀 Запуск продакшен сервисов..."
	docker-compose -f docker-compose.production.yml up -d
	@echo "✅ Продакшен запущен!"
	@echo ""
	@echo "🌐 Доступные адреса:"
	@echo "  • Основной сайт: https://gragert.ru/"
	@echo "  • API документация: https://gragert.ru/docs"
	@echo "  • N8N интерфейс: https://gragert.ru/n8n/"
	@echo ""
	@echo "🔐 N8N: настройте аккаунт при первом входе"

# Остановить продакшен сервисы
prod-down:
	@echo "🛑 Остановка продакшен сервисов..."
	docker-compose -f docker-compose.production.yml down

# Перезапустить продакшен сервисы
prod-restart: prod-down prod-up

# Логи продакшена
prod-logs:
	docker-compose -f docker-compose.production.yml logs -f

# Статус продакшен контейнеров
prod-status:
	@echo "📊 Статус продакшен контейнеров:"
	@docker-compose -f docker-compose.production.yml ps
