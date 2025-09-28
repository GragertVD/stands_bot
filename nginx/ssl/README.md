# SSL Сертификаты

## 📋 Необходимые файлы

В этой папке должны быть размещены SSL сертификаты для домена gragert.ru:

- **fullchain.pem** - Полная цепочка сертификатов
- **privkey.pem** - Приватный ключ

## 🔒 Установка сертификатов

### 1. Поместите файлы сертификатов

```bash
# Скопируйте ваши сертификаты в эту папку
cp /path/to/your/fullchain.pem nginx/ssl/
cp /path/to/your/privkey.pem nginx/ssl/
```

### 2. Установите правильные права доступа

```bash
# Права на сертификат (может читать все)
chmod 644 nginx/ssl/fullchain.pem

# Права на приватный ключ (только владелец может читать)
chmod 600 nginx/ssl/privkey.pem
```

## 🛠️ Получение SSL сертификатов

### Let's Encrypt (бесплатно)

```bash
# Установка certbot
sudo apt install certbot

# Получение сертификата
sudo certbot certonly --standalone -d gragert.ru -d www.gragert.ru

# Сертификаты будут в:
# /etc/letsencrypt/live/gragert.ru/fullchain.pem
# /etc/letsencrypt/live/gragert.ru/privkey.pem
```

### Коммерческий сертификат

Если у вас есть коммерческий SSL сертификат:

1. **fullchain.pem** должен содержать:
   - Ваш сертификат
   - Промежуточные сертификаты
   - Корневой сертификат

2. **privkey.pem** должен содержать приватный ключ

## ⚠️ Важные замечания

- **НЕ коммитьте реальные сертификаты в git!**
- Файлы сертификатов добавлены в .gitignore
- Регулярно обновляйте сертификаты (Let's Encrypt истекает через 90 дней)
- Храните резервные копии сертификатов в безопасном месте

## 🔍 Проверка сертификатов

### Проверка валидности сертификата

```bash
# Проверка информации о сертификате
openssl x509 -in fullchain.pem -text -noout

# Проверка срока действия
openssl x509 -in fullchain.pem -noout -dates

# Проверка соответствия ключа и сертификата
openssl x509 -noout -modulus -in fullchain.pem | openssl md5
openssl rsa -noout -modulus -in privkey.pem | openssl md5
# Хэши должны совпадать
```

### Тестирование SSL в браузере

После установки сертификатов:

1. Откройте https://gragert.ru в браузере
2. Проверьте что соединение защищено (зеленый замок)
3. Используйте онлайн инструменты как SSL Labs для детальной проверки

## 🔄 Автоматическое обновление Let's Encrypt

```bash
# Добавьте в crontab для автоматического обновления
sudo crontab -e

# Добавьте строку (обновление каждые 12 часов)
0 */12 * * * certbot renew --quiet && docker-compose -f /path/to/your/project/docker-compose.production.yml restart nginx
```

## 🆘 Устранение проблем

### Ошибка "SSL certificate problem"

1. Проверьте что файлы существуют и имеют правильные права
2. Проверьте что сертификат не истек
3. Убедитесь что сертификат выдан для правильного домена

### Ошибка "Mixed content"

Убедитесь что все ресурсы загружаются через HTTPS, а не HTTP.

### Nginx не стартует с SSL

Проверьте логи Nginx:
```bash
make prod-logs | grep nginx
```

Типичные причины:
- Неправильные пути к файлам
- Неправильные права доступа
- Поврежденные файлы сертификатов
