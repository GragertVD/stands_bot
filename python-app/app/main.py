"""
VK Teams Bot - Система с интеграцией N8N
Координирует работу VK Teams бота, API сервера и интеграцию с N8N
"""
import logging
import threading
import uvicorn

from .config import Config
from .vk_teams_bot import VKTeamsBot
from .webhook_handler import WebhookHandler
from .api_server import APIServer

logger = logging.getLogger(__name__)

def main():
    """Основная функция запуска приложения"""
    
    # Проверяем конфигурацию
    if not Config.validate():
        logger.error("❌ Некорректная конфигурация. Завершение работы.")
        return
    
    # Выводим информацию о конфигурации
    Config.log_config()
    
    # Создаем компоненты системы
    webhook_handler = WebhookHandler()
    vk_bot = VKTeamsBot(webhook_handler)
    api_server = APIServer()
    
    # Связываем компоненты
    api_server.set_bot_instance(vk_bot)
    
    # Запускаем long polling в отдельном потоке
    logger.info("🔄 Запускаем long polling...")
    polling_thread = threading.Thread(target=vk_bot.polling_loop, daemon=True)
    polling_thread.start()
    logger.info("🤖 VK Teams бот запущен в фоновом режиме")
    
    # Запускаем HTTP сервер
    logger.info(f"🌐 Запускаем HTTP сервер на порту {Config.SERVER_PORT}...")
    
    try:
        app = api_server.get_app()
        uvicorn.run(
            app,
            host=Config.SERVER_HOST,
            port=Config.SERVER_PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    finally:
        vk_bot.stop()
        logger.info("👋 Система остановлена")

if __name__ == "__main__":
    main()