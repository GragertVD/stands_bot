# 🧪 Примеры тестирования кнопок VK Teams

## 📝 Тестовые запросы

### 1. Простое сообщение с кнопками через N8N webhook

```bash
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "v.graget@vkteam.ru",
    "message": "🎯 Выберите действие:",
    "message_type": "text",
    "buttons": [
      {
        "text": "✅ Подтвердить",
        "callback_data": "confirm_action"
      },
      {
        "text": "❌ Отменить",
        "callback_data": "cancel_action"
      },
      {
        "text": "📖 Документация",
        "url": "https://teams.vk.com/botapi/tutorial/"
      }
    ]
  }'
```

### 2. Меню выбора с несколькими кнопками

```bash
curl -X POST http://localhost:8000/api/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "v.graget@vkteam.ru",
    "message": "🏪 Добро пожаловать в наш магазин!\n\nВыберите категорию товаров:",
    "buttons": [
      {"text": "👕 Одежда", "callback_data": "category_clothes"},
      {"text": "📱 Электроника", "callback_data": "category_electronics"},
      {"text": "📚 Книги", "callback_data": "category_books"},
      {"text": "🏠 Дом и сад", "callback_data": "category_home"},
      {"text": "🛒 Корзина", "callback_data": "show_cart"},
      {"text": "🆘 Поддержка", "callback_data": "support"}
    ]
  }'
```

### 3. Опрос пользователей

```bash
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "v.graget@vkteam.ru",
    "message": "⭐ Как вы оцениваете нашу новую функцию кнопок?",
    "buttons": [
      {"text": "⭐⭐⭐⭐⭐ Отлично!", "callback_data": "rating_5"},
      {"text": "⭐⭐⭐⭐ Хорошо", "callback_data": "rating_4"},
      {"text": "⭐⭐⭐ Нормально", "callback_data": "rating_3"},
      {"text": "⭐⭐ Плохо", "callback_data": "rating_2"},
      {"text": "⭐ Ужасно", "callback_data": "rating_1"}
    ]
  }'
```

### 4. Интерактивная поддержка

```bash
curl -X POST http://localhost:8000/api/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "v.graget@vkteam.ru",
    "message": "🆘 Центр поддержки\n\nКак мы можем вам помочь?",
    "buttons": [
      {"text": "🐛 Сообщить об ошибке", "callback_data": "report_bug"},
      {"text": "💡 Предложить идею", "callback_data": "suggest_feature"},
      {"text": "❓ Задать вопрос", "callback_data": "ask_question"},
      {"text": "📞 Связаться с оператором", "callback_data": "contact_operator"},
      {"text": "📖 База знаний", "url": "https://help.example.com"},
      {"text": "🏠 Главное меню", "callback_data": "main_menu"}
    ]
  }'
```

## 🔄 Ожидаемые ответы от бота

### Успешная отправка:
```json
{
  "status": "accepted",
  "chat_id": "v.graget@vkteam.ru",
  "message": "🎯 Выберите действие:",
  "message_type": "text",
  "timestamp": "2025-09-28T16:30:15.123456",
  "message_length": 20
}
```

### Логи в консоли:
```
📥 Получен webhook от N8N для чата v.graget@vkteam.ru: 🎯 Выберите действие:...
📤 Отправлено сообщение с 3 кнопками
🔘 С клавиатурой: {'inlineKeyboard': [[{'text': '✅ Подтвердить', 'callbackData': 'confirm_action'}], ...]}
✅ Сообщение с кнопками УСПЕШНО отправлено в чат v.graget@vkteam.ru
✅ Webhook сообщение доставлено в чат v.graget@vkteam.ru
```

## 🎮 Интерактивные команды бота

### Команда /start
Автоматически создает меню:
```
Привет! Я VK Teams бот с интеграцией N8N и поддержкой кнопок.

Выберите действие:

[❓ Справка] [📊 Статус]
[🧪 Тест эхо]
```

### Команда /status  
Показывает интерактивный статус:
```
🤖 Статус бота: Активен
📊 Активных чатов: 5
🔗 API URL: https://api.internal.myteam.mail.ru/bot/v1
📡 N8N Webhook: ✅ Настроен
🎯 Окружение: production

[🔄 Обновить] [❓ Справка]
[🧪 Тест эхо]
```

## 📊 Обработка нажатий

Когда пользователь нажимает кнопку, система:

1. **Логирует событие**:
```
🔘 Нажатие кнопки от Владимир Грагерт в чате v.graget@vkteam.ru: confirm_action
```

2. **Отправляет в N8N**:
```json
{
  "timestamp": "2025-09-28T16:30:45.123456",
  "source": "vk_teams", 
  "event_type": "callback_query",
  "data": {
    "callback_data": "confirm_action",
    "chat_id": "v.graget@vkteam.ru",
    "user_name": "Владимир Грагерт",
    "user_id": "v.graget@vkteam.ru",
    "query_id": "unique_query_id_123"
  }
}
```

3. **Выполняет действие** согласно callback_data
4. **Отвечает пользователю**:
```
✅ Действие подтверждено!
```

## 🌐 API Endpoints

### Новые endpoints:
- `POST /api/webhook` - прием webhook с кнопками от N8N
- `POST /api/send-message` - прямая отправка сообщений с кнопками  
- `GET /api/stats` - статистика с информацией о кнопках

### Проверка работы:
```bash
# Проверить статус системы
curl -s http://localhost:8000/health | jq .

# Получить статистику
curl -s http://localhost:8000/api/stats | jq .

# Посмотреть Swagger документацию
curl -s http://localhost:8000/docs
```

## 🎨 Форматы VK Teams

Согласно [документации VK Teams](https://teams.vk.com/botapi/tutorial/), поддерживаются:

### Callback кнопки:
```json
{
  "text": "Кнопка",
  "callbackData": "action_name"
}
```

### URL кнопки:
```json
{
  "text": "Ссылка", 
  "url": "https://example.com"
}
```

### Структура клавиатуры:
```json
{
  "inlineKeyboardMarkup": {
    "inlineKeyboard": [
      [{"text": "Кнопка 1", "callbackData": "btn1"}],
      [{"text": "Кнопка 2", "callbackData": "btn2"}]
    ]
  }
}
```

**Система полностью готова для работы с интерактивными кнопками VK Teams!** 🎉
