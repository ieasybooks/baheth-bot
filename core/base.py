import logging
import asyncio
from telegram import Update, error
from telegram.ext import ContextTypes

from .utils.api import ApiUtils

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


class Base:
    def __init__(self) -> None:
        # Only one class will inherit from this base, so the logger is initialized here
        self.api = ApiUtils()

    def add_update_user(self, command: str, user_id: int, users: dict[dict]):
        if (user_exists := users.get(user_id)):
            users[user_id]["command"] = command
        else:
            users[user_id] = {
                "command": command
            }

        print("\n\n\n\n", users, "\n\n\n\n")
        return users

    async def send_html_message(self, message: str, update: Update, context: ContextTypes.DEFAULT_TYPE, delay: int = 0) -> None:
        try:
            await update.message.reply_html(message)
            await asyncio.sleep(delay)
        except error.BadRequest as e:
            # The message is too long: 4096 chars is the limit
            mid = len(message) // 2
            await self.send_html_message(message[:mid], update, context)
            await self.send_html_message(message[mid:], update, context)
