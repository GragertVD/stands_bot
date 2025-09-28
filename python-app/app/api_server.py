"""
API Server - FastAPI приложение с интеграцией N8N
Упрощенная версия с сохранением всей функциональности
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .config import Config
from .webhook_handler import WebhookHandler, IncomingWebhookMessage

logger = logging.getLogger(__name__)

class APIServer:
    """FastAPI сервер для управления ботом и интеграцией с N8N"""
    
    def __init__(self):
        self.app = FastAPI(
            title="VK Teams Bot with N8N Integration",
            description="VK Teams бот с интеграцией N8N для автоматизации",
            version="2.0.0"
        )
        self.webhook_handler = WebhookHandler()
        self.vk_bot_instance = None
        self._setup_routes()
    
    def set_bot_instance(self, bot_instance):
        """Установить экземпляр бота"""
        self.vk_bot_instance = bot_instance
        
    def _setup_routes(self):
        """Настроить маршруты API"""
        
        @self.app.get("/")
        async def root():
            """Основная информация о системе"""
            active_chats = self.vk_bot_instance.get_active_chats() if self.vk_bot_instance else {}
            webhook_stats = self.webhook_handler.get_webhook_stats()
            
            return {
                "bot": "VK Teams Bot with N8N Integration",
                "version": "2.0.0",
                "status": "running" if self.vk_bot_instance and self.vk_bot_instance.bot_running else "stopped",
                "environment": Config.ENVIRONMENT,
                "active_chats": len(active_chats),
                "n8n_integration": webhook_stats["n8n_webhook_configured"],
                "endpoints": {
                    "health": "/health",
                    "chats": "/chats",
                    "webhook": "/api/webhook",
                    "docs": "/docs"
                },
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/health")
        async def health_check():
            """Проверка здоровья всей системы"""
            active_chats = self.vk_bot_instance.get_active_chats() if self.vk_bot_instance else {}
            webhook_stats = self.webhook_handler.get_webhook_stats()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "vk_bot": {
                        "running": self.vk_bot_instance.bot_running if self.vk_bot_instance else False,
                        "token_configured": bool(Config.BOT_TOKEN),
                        "active_chats": len(active_chats)
                    },
                    "n8n_integration": {
                        "webhook_configured": webhook_stats["n8n_webhook_configured"],
                        "stats": webhook_stats.get("stats", {})
                    },
                    "api_server": {
                        "port": Config.SERVER_PORT,
                        "environment": Config.ENVIRONMENT
                    }
                }
            }

        @self.app.get("/chats")
        async def get_active_chats():
            """Получить информацию об активных чатах"""
            if not self.vk_bot_instance:
                return {
                    "total_chats": 0,
                    "chats": {},
                    "error": "Bot instance not initialized"
                }
            
            active_chats = self.vk_bot_instance.get_active_chats()
            
            return {
                "total_chats": len(active_chats),
                "chats": active_chats,
                "timestamp": datetime.now().isoformat()
            }

        @self.app.post("/api/webhook")
        async def handle_incoming_webhook(message: IncomingWebhookMessage):
            """
            Принимать входящие сообщения от N8N
            и отправлять их пользователю в VK Teams
            """
            if not self.vk_bot_instance:
                logger.error("❌ Бот не инициализирован")
                raise HTTPException(status_code=500, detail="Bot not initialized")

            # Обработать webhook
            result = self.webhook_handler.process_incoming_webhook(message)
            
            if result["status"] == "error":
                raise HTTPException(status_code=400, detail=result["error"])

            # Проверить активные чаты
            active_chats = self.vk_bot_instance.get_active_chats()
            if message.chat_id not in active_chats:
                logger.warning(f"⚠️ Чат {message.chat_id} не найден в активных чатах")

            # Отправить сообщение в VK Teams
            success = self.vk_bot_instance.send_text(message.chat_id, message.message)

            if success:
                logger.info(f"✅ Webhook сообщение доставлено в чат {message.chat_id}")
                return JSONResponse(content=result, status_code=200)
            else:
                logger.error(f"❌ Не удалось доставить сообщение в чат {message.chat_id}")
                raise HTTPException(status_code=500, detail="Failed to send message to VK Teams")

        @self.app.get("/api/stats")
        async def get_stats():
            """Получить детальную статистику системы"""
            active_chats = self.vk_bot_instance.get_active_chats() if self.vk_bot_instance else {}
            webhook_stats = self.webhook_handler.get_webhook_stats()
            
            # Подсчет статистики по чатам
            total_messages = sum(chat.get('message_count', 0) for chat in active_chats.values())
            
            return {
                "system_status": {
                    "bot_running": self.vk_bot_instance.bot_running if self.vk_bot_instance else False,
                    "environment": Config.ENVIRONMENT,
                    "uptime": datetime.now().isoformat()
                },
                "chat_stats": {
                    "total_active_chats": len(active_chats),
                    "total_messages_processed": total_messages,
                    "chats": active_chats
                },
                "n8n_integration": webhook_stats,
                "config": {
                    "server_host": Config.SERVER_HOST,
                    "server_port": Config.SERVER_PORT,
                    "poll_time": Config.POLL_TIME,
                    "bot_api_url": Config.BOT_API_URL
                },
                "timestamp": datetime.now().isoformat()
            }

    def get_app(self) -> FastAPI:
        """Получить FastAPI приложение"""
        return self.app
