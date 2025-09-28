"""
Конфигурация системы VK Teams Bot + N8N
"""
import os
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
log_level = logging.DEBUG if os.getenv("DEBUG", "false").lower() == "true" else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Config:
    """Класс конфигурации приложения"""
    
    # VK Teams Bot настройки
    BOT_TOKEN = os.getenv("VK_TEAMS_BOT_TOKEN", "")
    BOT_API_URL = os.getenv("VK_TEAMS_API_URL", "https://api.internal.myteam.mail.ru/bot/v1").rstrip('/')
    
    # N8N интеграция
    N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")
    
    # HTTP сервер настройки
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
    
    # Redis настройки (для интеграции с N8N)
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    
    # Настройки long polling
    POLL_TIME = int(os.getenv("POLL_TIME", "30"))  # секунд
    
    # Окружение
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    @classmethod
    def validate(cls) -> bool:
        """Проверить корректность конфигурации"""
        if not cls.BOT_TOKEN:
            logging.error("❌ VK_TEAMS_BOT_TOKEN не установлен в переменных окружения")
            return False
        
        if not cls.BOT_API_URL:
            logging.error("❌ VK_TEAMS_API_URL не установлен в переменных окружения")
            return False
            
        return True
    
    @classmethod
    def log_config(cls):
        """Вывести информацию о конфигурации"""
        logging.info("🚀 Запуск VK Teams Bot с интеграцией N8N...")
        logging.info(f"🔗 Токен: {cls.BOT_TOKEN[:10]}...{cls.BOT_TOKEN[-4:] if len(cls.BOT_TOKEN) > 14 else 'короткий'}")
        logging.info(f"🔗 API URL: {cls.BOT_API_URL}")
        
        if cls.N8N_WEBHOOK_URL:
            logging.info(f"📡 N8N Webhook: {cls.N8N_WEBHOOK_URL}")
        else:
            logging.info("📡 N8N Webhook: НЕ НАСТРОЕН")
            
        logging.info(f"🌐 HTTP порт: {cls.SERVER_PORT}")
        logging.info(f"🗃️ Redis: {cls.REDIS_URL}")
        logging.info(f"🎯 Окружение: {cls.ENVIRONMENT}")
        logging.info("✅ Система готова к запуску")
