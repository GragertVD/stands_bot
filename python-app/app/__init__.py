"""
VK Teams Bot Application - Модульная архитектура
"""

__version__ = "2.0.0"

from .main import main
from .config import Config
from .vk_teams_bot import VKTeamsBot
from .webhook_handler import WebhookHandler
from .api_server import APIServer

__all__ = ["main", "Config", "VKTeamsBot", "WebhookHandler", "APIServer"]