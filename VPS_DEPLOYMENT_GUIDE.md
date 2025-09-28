# Полная инструкция развертывания VK Teams Bot + N8N на VPS

Пошаговое руководство развертывания системы на VPS сервере с HTTPS.

## 📋 Требования к серверу

- **Операционная система**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: минимум 2GB, рекомендуется 4GB
- **CPU**: минимум 2 ядра
- **Диск**: минимум 10GB свободного места
- **Сеть**: Статический IP адрес и доменное имя

## 🎯 Что будет развернуто

- **VK Teams Bot** - эхо-бот с интеграцией N8N
- **N8N** - платформа автоматизации workflows
- **Nginx** - реверс-прокси с SSL терминацией
- **Redis** - кэширование и обмен данными
- **SSL сертификаты** - автоматическое получение через Let's Encrypt

## 🚀 Шаг 1: Подготовка сервера

### Подключение к серверу

```bash
# Подключаемся к VPS
ssh root@your-server-ip
# или
ssh username@your-server-ip
```

### Обновление системы

```bash
# Ubuntu/Debian
apt update && apt upgrade -y

# CentOS/RHEL
dnf update -y
```

### Установка необходимых пакетов

```bash
# Ubuntu/Debian
apt install -y curl wget git nano htop

# CentOS/RHEL  
dnf install -y curl wget git nano htop
```

## 🐳 Шаг 2: Установка Docker

### Docker Engine

```bash
# Загружаем и устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Добавляем пользователя в группу docker (если не root)
usermod -aG docker $USER

# Включаем Docker в автозагрузку
systemctl enable docker
systemctl start docker

# Проверяем установку
docker --version
```

### Docker Compose

```bash
# Устанавливаем Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Проверяем установку
docker-compose --version
```

## 🌐 Шаг 3: Настройка домена и DNS

### Настройка DNS записей

В панели управления вашего домена создайте записи:

```
A    yourdomain.com      YOUR_SERVER_IP
A    www.yourdomain.com  YOUR_SERVER_IP
```

### Проверка DNS

```bash
# Проверяем, что домен указывает на сервер
nslookup yourdomain.com
dig yourdomain.com
```

## 📥 Шаг 4: Развертывание приложения

### Клонирование проекта

```bash
# Клонируем проект в домашнюю директорию
cd /root  # или cd /home/username
git clone <your-repository-url> vk-teams-bot-system
cd vk-teams-bot-system
```

### Настройка переменных окружения

```bash
# Создаем .env файл из продакшн шаблона
cp production.env .env

# Редактируем конфигурацию
nano .env
```

**ОБЯЗАТЕЛЬНО измените в .env:**

```bash
# VK Teams Bot - УКАЖИТЕ ВАШИ ДАННЫЕ!
VK_TEAMS_BOT_TOKEN=YOUR_REAL_BOT_TOKEN_HERE

# Домен - УКАЖИТЕ ВАШ ДОМЕН!
DOMAIN=yourdomain.com
N8N_HOST=yourdomain.com

# N8N пароль - СМЕНИТЕ НА БЕЗОПАСНЫЙ!
N8N_BASIC_AUTH_PASSWORD=YourSecureN8NPassword2024!

# Redis пароль - СМЕНИТЕ НА БЕЗОПАСНЫЙ!  
REDIS_PASSWORD=YourSecureRedisPassword2024!

# Разрешенные хосты
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🔒 Шаг 5: Получение SSL сертификатов

### Автоматическое получение через Certbot

```bash
# Устанавливаем Certbot
# Ubuntu/Debian
apt install -y certbot

# CentOS/RHEL
dnf install -y certbot

# Получаем SSL сертификаты (замените на ваш домен!)
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Копируем сертификаты в проект
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Устанавливаем правильные права
chmod 644 nginx/ssl/fullchain.pem
chmod 600 nginx/ssl/privkey.pem
```

### Настройка автообновления сертификатов

```bash
# Добавляем задание в cron для автообновления
echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'cd /root/vk-teams-bot-system && docker-compose -f docker-compose.production.yml restart nginx'" | crontab -

# Проверяем crontab
crontab -l
```

## 🔧 Шаг 6: Настройка Nginx конфигурации

### Обновление конфигурации для вашего домена

```bash
# Редактируем продакшн конфигурацию Nginx
nano nginx/conf.d/production.conf
```

**Измените в файле все вхождения `gragert.ru` на ваш домен:**

```nginx
server_name yourdomain.com www.yourdomain.com;
```

Используйте поиск и замену в nano: `Ctrl+\` → введите `gragert.ru` → `yourdomain.com` → `A` (заменить все)

## 🛡️ Шаг 7: Настройка файрвола

### Ubuntu (ufw)

```bash
# Разрешаем необходимые порты
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP (для редиректа)
ufw allow 443/tcp   # HTTPS
ufw enable

# Проверяем правила
ufw status verbose
```

### CentOS/RHEL (firewalld)

```bash
# Разрешаем порты
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload

# Проверяем
firewall-cmd --list-all
```

## 🚀 Шаг 8: Запуск приложения

### Создание необходимых директорий

```bash
# Создаем директории для данных
mkdir -p n8n/data
mkdir -p nginx/ssl

# Устанавливаем права для N8N
chown -R 1000:1000 n8n/data
```

### Сборка и запуск

```bash
# Собираем Docker образы
make prod-build

# Запускаем все сервисы
make prod-up

# Ждем 30 секунд для инициализации
sleep 30

# Проверяем статус
make prod-status
```

## ✅ Шаг 9: Проверка работоспособности

### Проверка сервисов

```bash
# Проверяем статус контейнеров
make prod-status

# Проверяем логи
make prod-logs

# Проверяем конкретные сервисы
docker-compose -f docker-compose.production.yml logs -f nginx
docker-compose -f docker-compose.production.yml logs -f python-app
```

### Проверка доступности

```bash
# Проверяем HTTP редирект на HTTPS
curl -I http://yourdomain.com

# Проверяем HTTPS
curl -I https://yourdomain.com/health

# Проверяем N8N
curl -I https://yourdomain.com/n8n/

# Проверяем API
curl https://yourdomain.com/health
```

### Веб-проверка

Откройте в браузере:

- **Основной сайт**: https://yourdomain.com/
- **API документация**: https://yourdomain.com/docs
- **N8N интерфейс**: https://yourdomain.com/n8n/
- **Health check**: https://yourdomain.com/health

## 🔐 Шаг 10: Безопасность и настройка автозапуска

### Создание systemd сервиса

```bash
# Создаем сервис для автозапуска
cat > /etc/systemd/system/vk-teams-bot.service << 'EOF'
[Unit]
Description=VK Teams Bot System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=/root/vk-teams-bot-system
ExecStart=/usr/local/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Активируем сервис
systemctl enable vk-teams-bot.service
systemctl start vk-teams-bot.service

# Проверяем статус
systemctl status vk-teams-bot.service
```

### Дополнительные настройки безопасности

```bash
# Настройка автоматических обновлений (Ubuntu)
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# Настройка SSH (рекомендуется)
nano /etc/ssh/sshd_config
# Установите: PasswordAuthentication no (если используете ключи)
# systemctl restart sshd

# Установка fail2ban для защиты от брутфорса
apt install -y fail2ban  # Ubuntu
# dnf install -y fail2ban  # CentOS
```

## 📊 Шаг 11: Мониторинг и обслуживание

### Полезные команды

```bash
# Логи системы
make prod-logs              # Все сервисы
journalctl -u docker        # Docker логи
journalctl -f               # Системные логи

# Управление сервисами
make prod-restart           # Перезапуск всех сервисов
make prod-down             # Остановка
make prod-up               # Запуск

# Обновление приложения
git pull origin main       # Получить обновления
make prod-down            # Остановить
make prod-build           # Пересобрать
make prod-up              # Запустить
```

### Мониторинг ресурсов

```bash
# Использование ресурсов контейнерами
docker stats

# Место на диске
df -h

# Память и CPU
htop

# Логи Nginx
tail -f /var/log/nginx/access.log
```

## 🔄 Настройка N8N Workflows

### Первоначальная настройка N8N

1. Откройте https://yourdomain.com/n8n/
2. Войдите с логином `admin` и паролем из `.env`
3. Создайте первый workflow:

### Пример webhook для VK Teams

**Создайте Workflow в N8N:**

1. **Webhook Trigger**
   - URL: будет автоматически: `https://yourdomain.com/webhook/vk-teams`
   - Method: POST

2. **Process Message Node** (Code)
   ```javascript
   const message = items[0].json;
   
   return [{
     json: {
       response: `Получил сообщение: ${message.data.text}`,
       chat_id: message.data.chat_id,
       user: message.data.user_name
     }
   }];
   ```

3. **HTTP Request Node** (отправка обратно в VK Teams)
   - URL: `https://yourdomain.com/api/webhook`
   - Method: POST
   - Body:
   ```json
   {
     "chat_id": "={{$json.chat_id}}",
     "message": "={{$json.response}}"
   }
   ```

## 🆘 Устранение неполадок

### Проблемы с SSL

```bash
# Проверка сертификатов
openssl x509 -in nginx/ssl/fullchain.pem -text -noout
openssl rsa -in nginx/ssl/privkey.pem -check

# Обновление сертификатов
certbot renew
cp /etc/letsencrypt/live/yourdomain.com/*.pem nginx/ssl/
make prod-restart
```

### 502 Bad Gateway

```bash
# Проверяем статус контейнеров
make prod-status

# Смотрим логи Nginx
docker-compose -f docker-compose.production.yml logs nginx

# Перезапускаем проблемный сервис
docker-compose -f docker-compose.production.yml restart python-app
```

### Бот не отвечает

```bash
# Проверяем логи Python приложения
docker-compose -f docker-compose.production.yml logs python-app

# Проверяем переменные окружения
docker-compose -f docker-compose.production.yml exec python-app env | grep VK

# Тестируем API
curl https://yourdomain.com/health
```

## ✅ Финальная проверка

После завершения развертывания у вас должно работать:

- ✅ **HTTPS сайт**: https://yourdomain.com/
- ✅ **VK Teams бот** отвечает на сообщения
- ✅ **N8N интерфейс**: https://yourdomain.com/n8n/
- ✅ **API документация**: https://yourdomain.com/docs
- ✅ **Автозапуск** после перезагрузки сервера
- ✅ **SSL сертификаты** автоматически обновляются

## 📱 Доступ к системе

После развертывания используйте:

### Пользователи
- **VK Teams бот**: отправьте `/start` боту
- **Веб интерфейс**: https://yourdomain.com/

### Администраторы  
- **N8N**: https://yourdomain.com/n8n/ (admin + ваш пароль)
- **API**: https://yourdomain.com/docs
- **Мониторинг**: https://yourdomain.com/health

---

## 🎉 Поздравляем!

Ваша система VK Teams Bot + N8N успешно развернута с HTTPS!

**Следующие шаги:**
1. Протестируйте бота в VK Teams
2. Создайте workflows в N8N
3. Настройте резервное копирование
4. Настройте мониторинг

Если возникнут проблемы, проверьте логи: `make prod-logs`
