"""
VK Teams Bot с интеграцией N8N
Обработка сообщений и отправка событий в N8N
"""
import logging
import requests
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

from .config import Config

logger = logging.getLogger(__name__)

class VKTeamsBot:
    """VK Teams Bot с поддержкой N8N интеграции"""
    
    def __init__(self, webhook_handler=None):
        self.token = Config.BOT_TOKEN
        self.api_url = Config.BOT_API_URL
        self.webhook_handler = webhook_handler
        self.last_event_id = 0
        self.session = requests.Session()
        self.bot_running = True
        self.active_chats = {}
        
    def get_events(self) -> Optional[Dict[str, Any]]:
        """Получить события через long polling"""
        url = f"{self.api_url}/events/get"
        params = {
            'token': self.token,
            'lastEventId': self.last_event_id,
            'pollTime': Config.POLL_TIME
        }

        try:
            logger.debug(f"📡 Long polling запрос к: {url}")
            response = self.session.get(url, params=params, timeout=Config.POLL_TIME + 5)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"📊 Получены события: {len(data.get('events', []))}")
                return data
            else:
                logger.error(f"❌ Ошибка API: статус {response.status_code}, ответ: {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.debug("⏱️ Таймаут long polling (нормально)")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Ошибка сетевого запроса: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"❌ Ошибка парсинга JSON: {e}")
            return None

    def send_text(self, chat_id: str, text: str) -> bool:
        """Отправить текстовое сообщение"""
        url = f"{self.api_url}/messages/sendText"
        data = {
            'token': self.token,
            'chatId': chat_id,
            'text': text
        }

        try:
            logger.debug(f"📤 Отправка сообщения в {chat_id}: {text[:50]}...")
            response = self.session.post(url, data=data)
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if response_data.get('ok', False):
                        logger.info(f"✅ Сообщение успешно отправлено в чат {chat_id}")
                        return True
                    else:
                        logger.error(f"❌ API вернул ошибку: {response_data}")
                        return False
                except json.JSONDecodeError:
                    logger.info(f"✅ Сообщение отправлено в чат {chat_id} (статус 200)")
                    return True
            else:
                logger.error(f"❌ Ошибка отправки: статус {response.status_code}, ответ: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Исключение при отправке: {e}")
            return False

    def handle_message(self, event: Dict[str, Any]):
        """Обработчик сообщений с интеграцией N8N"""
        try:
            payload = event.get('payload', {})
            chat = payload.get('chat', {})
            sender = payload.get('from', {})

            message_text = payload.get('text', '')
            chat_id = chat.get('chatId', '')
            user_name = f"{sender.get('firstName', '')} {sender.get('lastName', '')}"
            user_id = sender.get('userId', '')

            logger.info(f"💬 Сообщение от {user_name} в чате {chat_id}: {message_text}")
            
            # Сохраняем информацию об активном чате
            self.active_chats[chat_id] = {
                'user_name': user_name.strip(),
                'user_id': user_id,
                'last_message_time': datetime.now().isoformat(),
                'message_count': self.active_chats.get(chat_id, {}).get('message_count', 0) + 1
            }

            # Отправляем событие в N8N (если настроено)
            if self.webhook_handler:
                self.webhook_handler.send_to_n8n_webhook(event)

            # Игнорируем пустые сообщения
            if not message_text:
                return

            # Обработка команд
            if message_text == "/start":
                welcome_text = (
                    "👋 Привет! Я VK Teams бот с интеграцией N8N.\n"
                    "Отправь мне любое сообщение, и я:\n"
                    "• Отвечу эхом\n"
                    "• Перешлю событие в N8N для обработки"
                )
                self.send_text(chat_id, welcome_text)

            elif message_text == "/help":
                help_text = (
                    "📖 Доступные команды:\n"
                    "/start - начать работу с ботом\n"
                    "/help - показать эту справку\n"
                    "/status - показать статус бота и интеграций\n\n"
                    "Просто отправь мне любое сообщение, и я отправлю его обратно, "
                    "а также перешлю в N8N для дальнейшей обработки."
                )
                self.send_text(chat_id, help_text)
                
            elif message_text == "/status":
                n8n_status = "✅ Настроен" if Config.N8N_WEBHOOK_URL else "❌ Не настроен"
                status_text = (
                    f"🤖 Статус бота: Активен\n"
                    f"📊 Активных чатов: {len(self.active_chats)}\n"
                    f"🔗 API URL: {Config.BOT_API_URL}\n"
                    f"📡 N8N интеграция: {n8n_status}\n"
                    f"🎯 Окружение: {Config.ENVIRONMENT}"
                )
                self.send_text(chat_id, status_text)

            elif not message_text.startswith("/"):
                # Эхо-ответ для обычных сообщений
                echo_text = f"🔄 Эхо: {message_text}"
                self.send_text(chat_id, echo_text)

        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")

    def polling_loop(self):
        """Основной цикл long polling"""
        logger.info("🔄 Long polling запущен...")

        while self.bot_running:
            try:
                events = self.get_events()

                if events and 'events' in events:
                    logger.debug(f"📨 Получено {len(events['events'])} событий")
                    for event in events['events']:
                        event_id = event.get('eventId', 0)
                        event_type = event.get('type', '')

                        logger.debug(f"🎯 Событие ID: {event_id}, Тип: {event_type}")

                        if event_id > self.last_event_id:
                            self.last_event_id = event_id

                        if event_type == 'newMessage':
                            self.handle_message(event)
                        else:
                            logger.debug(f"⏭️ Пропускаем событие типа: {event_type}")

                time.sleep(1)

            except KeyboardInterrupt:
                logger.info("🛑 Получен сигнал остановки long polling")
                self.bot_running = False
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в polling loop: {e}")
                time.sleep(5)

    def stop(self):
        """Остановить бота"""
        self.bot_running = False
        logger.info("🛑 VK Teams бот остановлен")
        
    def get_active_chats(self) -> Dict[str, Any]:
        """Получить информацию об активных чатах"""
        return self.active_chats.copy()
