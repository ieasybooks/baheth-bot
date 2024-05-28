import os

from dotenv import load_dotenv

from bot import Bot


load_dotenv()


Bot(
    os.getenv('TELEGRAM_BOT_TOKEN'),
    os.getenv('BAHETH_API_BASE_URL'),
    os.getenv('MEDIA_ENDPOINT'),
    os.getenv('TRANSCRIPTIONS_SEARCH_ENDPOINT'),
    os.getenv('HADITHS_SEARCH_ENDPOINT'),
    os.getenv('SHAMELA_SEARCH_ENDPOINT'),
    os.getenv('BAHETH_API_TOKEN'),
).run()
