# 🔘 VK Teams Bot - Руководство по кнопкам

Система поддерживает отправку **inline-кнопок** в VK Teams согласно [официальной документации VK Teams Bot API](https://teams.vk.com/botapi/tutorial/).

## 📋 Возможности

### ✅ Поддерживаемые типы кнопок:
- **Callback кнопки** - выполняют действие при нажатии
- **URL кнопки** - открывают ссылку в браузере
- **Комбинированные клавиатуры** - несколько кнопок в рядах

### ✅ Интеграция с N8N:
- Отправка кнопок через webhook от N8N
- Получение событий нажатий кнопок в N8N
- Полная совместимость с автоматизацией

## 🚀 Использование

### 1. Отправка через N8N Webhook

```bash
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "user@vkteam.ru",
    "message": "Выберите действие:",
    "message_type": "text",
    "buttons": [
      {
        "text": "✅ Подтвердить",
        "callback_data": "confirm"
      },
      {
        "text": "❌ Отменить", 
        "callback_data": "cancel"
      },
      {
        "text": "🔗 Открыть ссылку",
        "url": "https://example.com"
      }
    ]
  }'
```

### 2. Прямая отправка через API

```bash
curl -X POST http://localhost:8000/api/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "user@vkteam.ru",
    "message": "Выберите опцию:",
    "buttons": [
      {"text": "Опция 1", "callback_data": "option_1"},
      {"text": "Опция 2", "callback_data": "option_2"}
    ]
  }'
```

### 3. Встроенные команды бота

Бот автоматически добавляет кнопки к командам:

- **`/start`** - показывает главное меню с кнопками
- **`/help`** - справка с интерактивными кнопками  
- **`/status`** - статус системы с кнопками управления
- **Эхо-сообщения** - включают кнопку "Повторить"

## 📚 Формат кнопок

### Callback кнопка
```json
{
  "text": "Название кнопки",
  "callback_data": "action_name"
}
```

### URL кнопка  
```json
{
  "text": "Открыть ссылку",
  "url": "https://example.com"
}
```

### Множественные кнопки
```json
{
  "chat_id": "user@vkteam.ru",
  "message": "Выберите:",
  "buttons": [
    {"text": "Кнопка 1", "callback_data": "btn1"},
    {"text": "Кнопка 2", "callback_data": "btn2"},
    {"text": "Кнопка 3", "callback_data": "btn3"},
    {"text": "Кнопка 4", "callback_data": "btn4"}
  ]
}
```

## 🔄 Обработка нажатий

При нажатии на кнопку бот:

1. **Логирует событие** с данными пользователя
2. **Отправляет в N8N** полную информацию о нажатии
3. **Выполняет действие** согласно callback_data
4. **Отвечает пользователю** подтверждением или результатом

### Пример обработки в боте:

```python
def handle_callback_query(self, event):
    callback_data = event['payload']['callbackData']
    
    if callback_data == "confirm":
        self.send_text(chat_id, "✅ Операция подтверждена!")
    elif callback_data == "cancel":
        self.send_text(chat_id, "❌ Операция отменена!")
```

## 🎯 N8N Интеграция

### Получение событий от VK Teams:

```json
{
  "timestamp": "2025-09-28T16:17:43.227355",
  "source": "vk_teams",
  "event_type": "callback_query",
  "data": {
    "callback_data": "confirm",
    "chat_id": "user@vkteam.ru",
    "user_name": "Владимир Грагерт",
    "user_id": "v.graget@vkteam.ru",
    "query_id": "abc123..."
  }
}
```

### Отправка кнопок из N8N:

Используйте HTTP Request ноду с URL: `http://bot:8000/api/webhook`

## 📱 Примеры интерфейсов

### Главное меню
```
Привет! Выберите действие:

[❓ Справка] [📊 Статус]
[🧪 Тест эхо]
```

### Меню статуса  
```
🤖 Статус бота: Активен
📊 Активных чатов: 5
🔗 API URL: https://api.internal.myteam.mail.ru/bot/v1

[🔄 Обновить] [❓ Справка]  
[🧪 Тест эхо]
```

### Эхо-ответ
```
Эхо: Ваше сообщение

[🔄 Повторить]
```

## 🛠️ Разработка

### Класс InlineKeyboard

```python
from app.bot import InlineKeyboard

# Создание клавиатуры
keyboard = InlineKeyboard()

# Добавление кнопок
keyboard.add_button("Кнопка 1", "callback_1")
keyboard.add_button("Ссылка", url="https://example.com")

# Добавление ряда кнопок
keyboard.add_row([
    {"text": "Да", "callback_data": "yes"},
    {"text": "Нет", "callback_data": "no"}
])

# Отправка
bot.send_text(chat_id, "Выберите:", keyboard)
```

### Упрощенный метод

```python
# Отправка с кнопками напрямую
buttons = [
    {"text": "Принять", "callback_data": "accept"},
    {"text": "Отклонить", "callback_data": "reject"}
]

bot.send_message_with_buttons(chat_id, "Принять заявку?", buttons)
```

## 🔍 Отладка

### Логи событий кнопок:
```
🔘 Нажатие кнопки от Владимир Грагерт в чате v.graget@vkteam.ru: confirm
📤 Отправлено сообщение с 2 кнопками
✅ Сообщение с кнопками УСПЕШНО отправлено в чат v.graget@vkteam.ru
```

### API Endpoints для тестирования:
- `GET /api/stats` - статистика с информацией о кнопках
- `POST /api/send-message` - тестовая отправка с кнопками
- `GET /docs` - Swagger документация API

## 🎉 Готовые сценарии

### Опрос пользователей
```json
{
  "message": "Оцените наш сервис:",
  "buttons": [
    {"text": "⭐⭐⭐⭐⭐", "callback_data": "rating_5"},
    {"text": "⭐⭐⭐⭐", "callback_data": "rating_4"},
    {"text": "⭐⭐⭐", "callback_data": "rating_3"},
    {"text": "⭐⭐", "callback_data": "rating_2"},
    {"text": "⭐", "callback_data": "rating_1"}
  ]
}
```

### Меню выбора
```json
{
  "message": "Выберите раздел:",
  "buttons": [
    {"text": "📊 Аналитика", "callback_data": "analytics"},
    {"text": "⚙️ Настройки", "callback_data": "settings"},
    {"text": "📞 Поддержка", "callback_data": "support"},
    {"text": "📖 Документация", "url": "https://docs.example.com"}
  ]
}
```

**Система готова к продуктивному использованию с полной поддержкой интерактивных кнопок VK Teams!** 🚀
