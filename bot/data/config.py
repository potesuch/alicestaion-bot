import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

ASSEMBLYAI_TOKEN = os.getenv('ASSEMBLYAI_TOKEN')

# Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 0)

WEB_SERVER_HOST = os.getenv('WEB_SERVER_HOST', '127.0.0.1')
WEB_SERVER_PORT = os.getenv('WEB_SERVER_PORT', '8000')

NGROK_HOST = os.getenv('NGROK_HOST')
NGROK_PORT = os.getenv('NGROK_PORT')

WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/webhook')
BASE_WEBHOOK_URL = os.getenv('BASE_WEBHOOK_URL')
