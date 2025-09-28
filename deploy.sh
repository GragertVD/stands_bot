#!/bin/bash

# Автоматический скрипт развертывания VK Teams Bot + N8N на VPS
# Использование: ./deploy.sh yourdomain.com

set -e  # Выход при любой ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для цветного вывода
print_color() {
    printf "${1}${2}${NC}\n"
}

# Функция для проверки команд
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_color $RED "❌ $1 не найден"
        return 1
    fi
    return 0
}

# Проверка аргументов
if [ $# -eq 0 ]; then
    print_color $RED "❌ Использование: ./deploy.sh yourdomain.com"
    print_color $YELLOW "Пример: ./deploy.sh mybot.example.com"
    exit 1
fi

DOMAIN=$1

print_color $BLUE "🚀 Развертывание VK Teams Bot System на домене: $DOMAIN"
print_color $BLUE "=================================================="

# Проверка что мы root или sudo
if [ "$EUID" -ne 0 ]; then
    print_color $RED "❌ Запустите скрипт с правами root или через sudo"
    exit 1
fi

# 1. Обновление системы
print_color $YELLOW "📦 Обновление системы..."
if check_command apt; then
    apt update && apt upgrade -y
    apt install -y curl wget git nano htop ufw
elif check_command dnf; then
    dnf update -y  
    dnf install -y curl wget git nano htop firewalld
else
    print_color $RED "❌ Неподдерживаемая система. Поддерживаются Ubuntu/Debian/CentOS/RHEL"
    exit 1
fi

# 2. Установка Docker
print_color $YELLOW "🐳 Установка Docker..."
if ! check_command docker; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Установка Docker Compose
print_color $YELLOW "🐳 Установка Docker Compose..."
if ! check_command docker-compose; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Проверка установки
print_color $GREEN "✅ Docker: $(docker --version)"
print_color $GREEN "✅ Docker Compose: $(docker-compose --version)"

# 3. Настройка файрвола
print_color $YELLOW "🛡️ Настройка файрвола..."
if check_command ufw; then
    ufw --force enable
    ufw allow 22/tcp   # SSH
    ufw allow 80/tcp   # HTTP
    ufw allow 443/tcp  # HTTPS
    print_color $GREEN "✅ UFW настроен"
elif check_command firewall-cmd; then
    systemctl enable firewalld
    systemctl start firewalld
    firewall-cmd --permanent --add-port=22/tcp
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    firewall-cmd --reload
    print_color $GREEN "✅ Firewalld настроен"
fi

# 4. Установка Certbot для SSL
print_color $YELLOW "🔒 Установка Certbot..."
if check_command apt; then
    apt install -y certbot
elif check_command dnf; then
    dnf install -y certbot
fi

# 5. Создание рабочей директории
WORK_DIR="/opt/vk-teams-bot-system"
print_color $YELLOW "📁 Создание рабочей директории: $WORK_DIR"

if [ -d "$WORK_DIR" ]; then
    print_color $YELLOW "⚠️ Директория уже существует. Обновляем..."
    cd $WORK_DIR
    git pull || print_color $YELLOW "⚠️ Не удалось обновить (возможно, есть локальные изменения)"
else
    print_color $BLUE "📥 Клонируем проект..."
    # Здесь нужно будет заменить на реальный URL репозитория
    echo "⚠️ ВАЖНО: Замените URL репозитория в скрипте на реальный!"
    echo "git clone <YOUR_REPOSITORY_URL> $WORK_DIR"
    # git clone https://github.com/username/vk-teams-bot-system $WORK_DIR
    mkdir -p $WORK_DIR
    cd $WORK_DIR
fi

# 6. Настройка переменных окружения
print_color $YELLOW "⚙️ Настройка конфигурации..."

# Создаем .env файл с заданным доменом
cat > .env << EOF
# VK Teams Bot Configuration
VK_TEAMS_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
VK_TEAMS_API_URL=https://api.internal.myteam.mail.ru/bot/v1

# N8N интеграция
N8N_WEBHOOK_URL=https://${DOMAIN}/webhook/vk-teams

# Server settings
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
POLL_TIME=30

# Redis (с паролем для безопасности)
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=SecureRedisPassword$(date +%Y)!

# N8N настройки для продакшена
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=SecureN8NPassword$(date +%Y)!
N8N_HOST=${DOMAIN}
N8N_PORT=443
N8N_PROTOCOL=https
N8N_PATH=/n8n/
WEBHOOK_URL=https://${DOMAIN}/
N8N_SECURE_COOKIE=true
N8N_COOKIE_SAME_SITE_POLICY=strict

# Домен и безопасность
DOMAIN=${DOMAIN}
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN}

# Environment
ENVIRONMENT=production
DEBUG=false
TIMEZONE=Europe/Moscow
EOF

print_color $GREEN "✅ Конфигурация создана"
print_color $RED "⚠️ ВАЖНО: Отредактируйте .env файл и укажите токен VK Teams бота:"
print_color $YELLOW "nano .env"

# 7. Создание директорий
print_color $YELLOW "📁 Создание необходимых директорий..."
mkdir -p n8n/data nginx/ssl

# 8. SSL сертификаты
print_color $YELLOW "🔒 Настройка SSL сертификатов для домена $DOMAIN..."

# Проверяем есть ли уже сертификаты в проекте
if [ -f "nginx/ssl/fullchain.pem" ] && [ -f "nginx/ssl/privkey.pem" ]; then
    print_color $GREEN "✅ Обнаружены готовые SSL сертификаты"
    
    # Проверяем валидность сертификатов
    if openssl x509 -in nginx/ssl/fullchain.pem -noout -checkend 0 >/dev/null 2>&1; then
        print_color $GREEN "✅ SSL сертификаты действительны"
    else
        print_color $RED "❌ SSL сертификаты истекли или некорректны"
        exit 1
    fi
    
    # Устанавливаем правильные права
    chmod 644 nginx/ssl/fullchain.pem
    chmod 600 nginx/ssl/privkey.pem
    
else
    print_color $YELLOW "📋 SSL сертификаты не найдены. Получаем через Let's Encrypt..."
    
    # Временно останавливаем веб-сервер если работает
    systemctl stop nginx 2>/dev/null || true
    systemctl stop apache2 2>/dev/null || true

    # Получаем сертификаты через Let's Encrypt
    if certbot certonly --standalone --agree-tos --register-unsafely-without-email -d $DOMAIN -d www.$DOMAIN; then
        # Копируем сертификаты
        cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
        cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/
        chmod 644 nginx/ssl/fullchain.pem
        chmod 600 nginx/ssl/privkey.pem
        print_color $GREEN "✅ SSL сертификаты получены через Let's Encrypt"
        
        # Настройка автообновления
        echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook 'cd $WORK_DIR && docker-compose -f docker-compose.production.yml restart nginx'" | crontab -
        print_color $GREEN "✅ Автообновление SSL настроено"
    else
        print_color $RED "❌ Не удалось получить SSL сертификаты"
        print_color $YELLOW "💡 Альтернативы:"
        print_color $YELLOW "1. Разместите готовые сертификаты в nginx/ssl/fullchain.pem и nginx/ssl/privkey.pem"
        print_color $YELLOW "2. Убедитесь что домен $DOMAIN указывает на IP этого сервера"
        print_color $YELLOW "3. Проверьте что порты 80 и 443 открыты в файрволе"
        print_color $YELLOW "4. Убедитесь что нет других веб-серверов на портах 80/443"
        print_color $YELLOW ""
        print_color $YELLOW "📖 Подробная инструкция: EXISTING_SSL_DEPLOYMENT.md"
        exit 1
    fi
fi

# 9. Настройка Nginx конфигурации под домен
print_color $YELLOW "🔧 Настройка Nginx для домена $DOMAIN..."

# Обновляем конфигурацию Nginx
if [ -f "nginx/conf.d/production.conf" ]; then
    sed -i "s/gragert\.ru/$DOMAIN/g" nginx/conf.d/production.conf
    print_color $GREEN "✅ Nginx конфигурация обновлена"
fi

# 10. Создание systemd сервиса
print_color $YELLOW "🔄 Настройка автозапуска..."

cat > /etc/systemd/system/vk-teams-bot.service << EOF
[Unit]
Description=VK Teams Bot System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=$WORK_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable vk-teams-bot.service
print_color $GREEN "✅ Автозапуск настроен"

# 11. Создание Makefile команд
print_color $YELLOW "⚙️ Создание удобных команд управления..."

cat > /usr/local/bin/botctl << 'EOF'
#!/bin/bash
cd /opt/vk-teams-bot-system

case "$1" in
    start)
        systemctl start vk-teams-bot
        ;;
    stop)
        systemctl stop vk-teams-bot
        ;;
    restart)
        systemctl restart vk-teams-bot
        ;;
    status)
        systemctl status vk-teams-bot
        docker-compose -f docker-compose.production.yml ps
        ;;
    logs)
        docker-compose -f docker-compose.production.yml logs -f
        ;;
    update)
        systemctl stop vk-teams-bot
        git pull
        docker-compose -f docker-compose.production.yml build --no-cache
        systemctl start vk-teams-bot
        ;;
    *)
        echo "Использование: botctl {start|stop|restart|status|logs|update}"
        ;;
esac
EOF

chmod +x /usr/local/bin/botctl
print_color $GREEN "✅ Команды управления созданы (используйте: botctl)"

# 12. Завершение
print_color $GREEN "\n🎉 Развертывание завершено!"
print_color $BLUE "\n📋 Что нужно сделать дальше:"
print_color $YELLOW "1. Отредактируйте .env файл и укажите токен бота:"
print_color $NC "   nano .env"
print_color $YELLOW "2. Запустите систему:"
print_color $NC "   botctl start"
print_color $YELLOW "3. Проверьте статус:"
print_color $NC "   botctl status"

print_color $BLUE "\n🌐 После запуска будет доступно:"
print_color $NC "   • Основной сайт: https://$DOMAIN/"
print_color $NC "   • N8N интерфейс: https://$DOMAIN/n8n/"
print_color $NC "   • API документация: https://$DOMAIN/docs"
print_color $NC "   • Health check: https://$DOMAIN/health"

print_color $BLUE "\n🔐 Данные для входа:"
print_color $NC "   • N8N логин: admin"
print_color $NC "   • N8N пароль: $(grep N8N_BASIC_AUTH_PASSWORD .env | cut -d'=' -f2)"

print_color $BLUE "\n🛠️ Команды управления:"
print_color $NC "   • botctl start    - запуск системы"
print_color $NC "   • botctl stop     - остановка системы"  
print_color $NC "   • botctl restart  - перезапуск системы"
print_color $NC "   • botctl status   - статус системы"
print_color $NC "   • botctl logs     - просмотр логов"
print_color $NC "   • botctl update   - обновление системы"

print_color $GREEN "\n✅ Готово к запуску!"
