# 🔘 VK Teams Bot - Кнопки ✅ РАБОТАЮЩЕЕ РЕШЕНИЕ

## 🎉 Подтвержденный формат кнопок

**УСПЕШНО ПРОТЕСТИРОВАНО** - кнопки отображаются и работают в VK Teams!

## 🚀 Как отправить кнопки

### 1. Через N8N webhook

```bash
curl -X POST http://localhost:8000/api/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "user@vkteam.ru",
    "message": "Выберите действие:",
    "inline_keyboard_markup": {
      "inlineKeyboard": [
        [
          {"text": "✅ Да", "callbackData": "yes"},
          {"text": "❌ Нет", "callbackData": "no"}
        ],
        [
          {"text": "🌐 VK.com", "url": "https://vk.com"}
        ]
      ]
    }
  }'
```

### 2. Через API send-message

```bash
curl -X POST http://localhost:8000/api/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": "user@vkteam.ru",
    "message": "Тест кнопок:",
    "inline_keyboard_markup": {
      "inlineKeyboard": [
        [{"text": "Кнопка", "callbackData": "test_btn"}]
      ]
    }
  }'
```

## 📝 Правильный формат

**Поле:** `inline_keyboard_markup` - JSON объект (не строка!)
**Структура:**

```json
{
  "inlineKeyboard": [
    [
      {"text": "Текст кнопки", "callbackData": "данные_для_callback"},
      {"text": "Кнопка 2", "callbackData": "action2"}
    ],
    [
      {"text": "URL кнопка", "url": "https://example.com"}
    ]
  ]
}
```

## 🎯 Основной сценарий использования

### Кнопка с callback (рекомендуемый формат):

```json
{
  "chat_id": "user@vkteam.ru",
  "message": "Выберите опцию:",
  "inline_keyboard_markup": {
    "inlineKeyboard": [
      [
        {"text": "Подтвердить", "callbackData": "confirm_order_12345"},
        {"text": "Отменить", "callbackData": "cancel_order_12345"}
      ]
    ]
  }
}
```

**Как это работает:**
1. Пользователь видит кнопки "Подтвердить" и "Отменить"
2. При нажатии на "Подтвердить" → отправляется `confirm_order_12345`
3. При нажатии на "Отменить" → отправляется `cancel_order_12345`
4. Бот получает событие `callbackQuery` с этими данными

## 🔧 Техническая реализация

**VK Teams ожидает:**
- Поле `inlineKeyboardMarkup` в form data
- Значение: JSON-строка с массивом массивов кнопок

**Код бота делает:**
```python
# Получает объект {"inlineKeyboard": [...]}
keyboard_obj = json.loads(inline_keyboard_markup)
# Извлекает массив кнопок и передает в API
data['inlineKeyboardMarkup'] = json.dumps(keyboard_obj['inlineKeyboard'])
```

## ✅ Поддерживаемые типы кнопок

### 1. Callback кнопка (основной тип)
```json
{"text": "Подтвердить", "callbackData": "confirm"}
```

### 2. URL кнопка
```json
{"text": "🌐 Открыть сайт", "url": "https://vk.com"}
```

## 📱 Примеры использования

### Меню выбора
```json
{
  "inline_keyboard_markup": {
    "inlineKeyboard": [
      [{"text": "📊 Статистика", "callbackData": "stats"}],
      [{"text": "⚙️ Настройки", "callbackData": "settings"}],
      [{"text": "❓ Помощь", "callbackData": "help"}]
    ]
  }
}
```

### Да/Нет диалог
```json
{
  "inline_keyboard_markup": {
    "inlineKeyboard": [
      [
        {"text": "👍 Да", "callbackData": "yes"},
        {"text": "👎 Нет", "callbackData": "no"}
      ]
    ]
  }
}
```

### Числовая клавиатура
```json
{
  "inline_keyboard_markup": {
    "inlineKeyboard": [
      [
        {"text": "1", "callbackData": "num_1"},
        {"text": "2", "callbackData": "num_2"},
        {"text": "3", "callbackData": "num_3"}
      ],
      [
        {"text": "4", "callbackData": "num_4"},
        {"text": "5", "callbackData": "num_5"},
        {"text": "6", "callbackData": "num_6"}
      ]
    ]
  }
}
```

## 🔄 Обработка нажатий

При нажатии кнопки:
1. **Бот получает** событие `callbackQuery`
2. **Логирует** нажатие: `"Нажатие кнопки от {user}: {callbackData}"`
3. **Отправляет в N8N** (если настроен)
4. **Отвечает пользователю** подтверждением

## 🎨 Цвета кнопок

**Вопрос:** Можно ли менять цвета кнопок в VK Teams?

На текущий момент в базовом формате не обнаружены параметры цветов. Возможные варианты:
- Использовать emoji для визуального различия: ✅❌🔵🟡
- Исследовать дополнительные параметры VK Teams API

## 🚨 Важные замечания

1. **Формат данных:** `inline_keyboard_markup` должно быть JSON-объектом, не строкой
2. **Структура:** Обязательно поле `inlineKeyboard` с массивом массивов
3. **Callback данные:** Используйте осмысленные идентификаторы
4. **URL кнопки:** Работают для внешних ссылок

---

**✅ Этот формат РАБОТАЕТ в VK Teams!** 🎉