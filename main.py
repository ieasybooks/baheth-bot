import os
from dotenv import load_dotenv

from bot.bot import Bot

load_dotenv()

TESTING_TOKEN = os.getenv("TOKEN")

bot = Bot(TESTING_TOKEN)

bot.run()
