import os
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters
from datetime import timedelta

from core.base import Base
from .vars import *


class Bot(Base):
    def __init__(self, token) -> None:
        super().__init__()
        self.token = token

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        first_name = update.message.from_user.first_name
        await self.send_html_message(first_name, update=update, context=context)

    async def hadith(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global users
        user_id = update.message.from_user.id
        users = self.add_update_user('hadith', user_id, users)

    async def shamela(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global users
        user_id = update.message.from_user.id
        users = self.add_update_user('shamela', user_id, users)

    async def tafrigh(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global users
        user_id = update.message.from_user.id
        users = self.add_update_user('tafrigh', user_id, users)
        await self.send_html_message(tafrigh_message, update, context)

    async def tafrigh_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        global users
        user_id = update.message.from_user.id
        users = self.add_update_user('tafrigh_search', user_id, users)
        await self.send_html_message(tafrigh_message, update, context)

    async def text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Responisble for text messages"""
        global users
        user_id = update.message.from_user.id

        if (user := users.get(user_id)):
            match user["command"]:
                case 'hadith':
                    response_json = self.api.get(
                        hadith_api, params={
                            "query": update.message.text
                        }, return_type="json")

                    for hadith in response_json.get("semantic_search_results")[:limit]:
                        title = hadith.get('book').get('title')

                        isnad = hadith.get('isnad', "")

                        matn = hadith.get('matn', "")
                        grade = hadith.get('grade')
                        breadcrumb = hadith['breadcrumb']
                        inline_text = "صفحة الحديث في باحث"
                        link = hadith.get('link')

                        message = f"<b>{title}</b>\n\n{isnad}{matn}  <i>({grade})</i> \n\n {breadcrumb} \n\n<a href='{link}'>{inline_text}</a>"
                        await self.send_html_message(message, update, context)

                case 'shamela':
                    response_json = self.api.get(
                        shamela_api, params={
                            "query": update.message.text
                        }, return_type="json")

                    for result in response_json['semantic_search_results'][:limit]:
                        print(result)
                        title = result.get('book')('title')
                        authors = '\n'.join(
                            author['name'] for author in result['authors'])
                        page = result.get('page')
                        link = result.get('link')
                        preview = result.get('preview')
                        inline_text = "رابط الصفحة في باحث"

                        message = f"<b>{title}</b>\n<i>{authors}</i>\nصفحة: {page}\n\n {preview} \n\n<a href='{link}'>{inline_text}</a>"
                        await self.send_html_message(message, update, context)

                case 'tafrigh':
                    response_json = self.api.get(
                        tafrigh_api, params={
                            "reference_id": update.message.text,
                            "reference_type": "youtube_link"
                        }, return_type="json")
                    transcription_link = response_json["transcription_link"]
                    message = f"[]({transcription_link})"

                    await update.message.reply_markdown_v2(message)

                case 'tafrigh_search':
                    response_json = self.api.get(tafrigh_search_api, params={
                        "query": update.message.text
                    }, return_type="json")

                    for result in response_json.get('classical_search_results')[:limit]:
                        print(f"\n\n{result}")
                        title = result.get('medium').get('title')
                        speakers = '\n'.join(speaker.get('name')
                                             for speaker in result.get('speakers'))
                        playlist = result.get('playlist').get('title')
                        content = result.get('content')
                        start_time = str(
                            timedelta(seconds=result.get('start_time')))
                        end_time = str(
                            timedelta(seconds=result.get('end_time')))
                        link = result.get('link')
                        inline_text = "رابط الصفحة في باحث"

                        message = f"<b>{title}</b>\n<i>{speakers} | {playlist}</i>\n\n{content}\n\nمن ({start_time}) إلى ({end_time})\n\n<a href='{link}'>{inline_text}</a>"
                        await self.send_html_message(message, update, context)

            del users[user_id]

        else:
            await update.message.reply_text(user_does_not_exist_message)

    def run(self):
        app = ApplicationBuilder().token(self.token).build()

        app.add_handler(CommandHandler('start', self.start))
        app.add_handler(CommandHandler('hadith', self.hadith))
        app.add_handler(CommandHandler('shamela', self.shamela))
        app.add_handler(CommandHandler('tafrigh', self.tafrigh))
        app.add_handler(CommandHandler('tafrigh_search', self.tafrigh_search))

        app.add_handler(MessageHandler(filters.TEXT, self.text))

        app.run_polling()
