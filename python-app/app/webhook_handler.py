"""
Webhook Handler - обработка интеграции с N8N
Упрощенная версия без избыточности
"""
import logging
import requests
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from .config import Config

logger = logging.getLogger(__name__)

class IncomingWebhookMessage(BaseModel):
    """Модель для входящего webhook сообщения от N8N"""
    chat_id: str
    message: str
    message_type: str = "text"
    inline_keyboard_markup: Optional[Dict[str, Any]] = None  # JSON объект с клавиатурой VK Teams

class WebhookHandler:
    """Обработчик webhooks для интеграции с N8N"""
    
    def __init__(self):
        self.n8n_webhook_url = Config.N8N_WEBHOOK_URL
        self.session = requests.Session()
        self.stats = {
            'messages_sent_to_n8n': 0,
            'messages_received_from_n8n': 0,
            'last_n8n_send': None,
            'last_n8n_receive': None
        }
        
    def send_to_n8n_webhook(self, event_data: Dict[str, Any]) -> bool:
        """Отправить событие VK Teams в N8N"""
        if not self.n8n_webhook_url:
            logger.debug("⚠️ N8N_WEBHOOK_URL не настроен, пропускаем отправку")
            return False

        try:
            # Подготавливаем структурированные данные для N8N
            payload = event_data.get('payload', {})
            event_type = event_data.get('type', 'new_message')  # Используем реальный тип события
            
            # Извлекаем chat_id в зависимости от типа события
            if event_type == 'callbackQuery':
                chat_id = payload.get('message', {}).get('chat', {}).get('chatId', '')
            else:
                chat_id = payload.get('chat', {}).get('chatId', '')
            
            webhook_data = {
                "timestamp": datetime.now().isoformat(),
                "source": "vk_teams",
                "event_type": event_type,
                "data": {
                    "text": payload.get('text', ''),
                    "chat_id": chat_id,
                    "user_name": f"{payload.get('from', {}).get('firstName', '')} {payload.get('from', {}).get('lastName', '')}".strip(),
                    "user_id": payload.get('from', {}).get('userId', ''),
                    "timestamp": payload.get('timestamp', 0),
                    "msg_id": payload.get('msgId', ''),
                    "callback_data": payload.get('callbackData')  # Добавляем данные кнопки
                }
            }
            
            logger.info(f"➡️ Отправляем событие в N8N: {self.n8n_webhook_url}")
            logger.debug(f"📦 Данные: {json.dumps(webhook_data, ensure_ascii=False, indent=2)[:200]}...")
            
            response = self.session.post(
                self.n8n_webhook_url, 
                json=webhook_data, 
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                self.stats['messages_sent_to_n8n'] += 1
                self.stats['last_n8n_send'] = datetime.now().isoformat()
                logger.info(f"✅ Событие успешно отправлено в N8N")
                return True
            else:
                logger.error(f"❌ N8N вернул ошибку: статус {response.status_code}, ответ: {response.text[:200]}...")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("❌ Таймаут при отправке в N8N")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Сетевая ошибка при отправке в N8N: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка webhook: {e}")
            return False

    def process_incoming_webhook(self, message: IncomingWebhookMessage) -> Dict[str, Any]:
        """Обработать входящий webhook от N8N"""
        try:
            logger.info(f"📥 Получен webhook от N8N для чата {message.chat_id}: {message.message[:50]}...")
            
            self.stats['messages_received_from_n8n'] += 1
            self.stats['last_n8n_receive'] = datetime.now().isoformat()
            
            return {
                "status": "accepted",
                "chat_id": message.chat_id,
                "message": message.message,
                "message_type": message.message_type,
                "timestamp": datetime.now().isoformat(),
                "message_length": len(message.message)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки входящего webhook: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_webhook_stats(self) -> Dict[str, Any]:
        """Получить статистику webhook интеграции"""
        return {
            "n8n_webhook_configured": bool(self.n8n_webhook_url),
            "n8n_webhook_url": self.n8n_webhook_url if self.n8n_webhook_url else "Not configured",
            "webhook_handler_status": "active",
            "stats": self.stats.copy()
        }
