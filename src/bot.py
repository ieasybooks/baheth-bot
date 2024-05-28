from datetime import timedelta
from typing import Self

from requests import get
from telegram import Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

from constants import COMMAND_MESSAGES, MESSAGE_LIMIT, REPLY_TEMPLATES, RESULTS_LIMIT


class Bot:
    def __init__(
        self,
        telegram_bot_token: str,
        baheth_api_base_url: str,
        media_endpoint: str,
        transcriptions_search_endpoint: str,
        hadiths_search_endpoint: str,
        shamela_search_endpoint: str,
        baheth_api_token: str,
    ) -> Self:
        super().__init__()

        self.users = dict()

        self.telegram_bot_token = telegram_bot_token
        self.baheth_api_base_url = baheth_api_base_url
        self.media_endpoint = media_endpoint
        self.transcriptions_search_endpoint = transcriptions_search_endpoint
        self.hadiths_search_endpoint = hadiths_search_endpoint
        self.shamela_search_endpoint = shamela_search_endpoint
        self.baheth_api_token = baheth_api_token


    def run(self) -> None:
        app = ApplicationBuilder().token(self.telegram_bot_token).build()

        app.add_handler(CommandHandler('start', self.start))
        app.add_handler(CommandHandler('tafrigh', self.tafrigh))
        app.add_handler(CommandHandler('transcriptions', self.transcriptions))
        app.add_handler(CommandHandler('hadiths', self.hadiths))
        app.add_handler(CommandHandler('shamela', self.shamela))

        app.add_handler(MessageHandler(filters.TEXT, self.text_handler))

        app.run_polling()


    async def start(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'start')


    async def tafrigh(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'tafrigh')


    async def transcriptions(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'transcriptions')


    async def hadiths(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'hadiths')


    async def shamela(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'shamela')


    async def text_handler(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id

        if (command := self.users.get(user_id)):
            match command:
                case 'tafrigh':
                    await self.__tafrigh_handler(update)
                case 'transcriptions':
                    await self.__transcriptions_handler(update)
                case 'hadiths':
                    await self.__hadiths_handler(update)
                case 'shamela':
                    await self.__shamela_handler(update)
        else:
            await update.message.reply_text(COMMAND_MESSAGES['no_command_selected'])


    async def __command_reply_handler(self, update: Update, command: str) -> None:
        self.users[update.message.from_user.id] = command
        await update.message.reply_html(COMMAND_MESSAGES[command])


    async def __tafrigh_handler(self, update: Update) -> None:
        response = get(
            self.baheth_api_base_url + self.media_endpoint,
            params={
                'reference_id': update.message.text,
                'reference_type': 'youtube_link',
            },
            timeout=10,
        )

        if response.status_code == 404:
            await update.message.reply_text(COMMAND_MESSAGES['medium_not_found'])
        elif response.status_code == 200:
            response = response.json()

            await update.message.reply_html(
                REPLY_TEMPLATES['tafrigh'].format(
                    response['title'],
                    # '، '.join([speaker['name'] for speaker in response['speakers']]),
                    # response['playlist']['title'],
                    response['link'],
                    response['transcription_link'],
                ),
            )
        else:
            await update.message.reply_text(COMMAND_MESSAGES['something_went_wrong'])


    async def __transcriptions_handler(self, update: Update) -> None:
        await update.message.reply_text(COMMAND_MESSAGES['wait_for_search'])

        response = get(
            self.baheth_api_base_url + self.transcriptions_search_endpoint,
            params={
                'token': self.baheth_api_token,
                'query': update.message.text,
            },
            timeout=10,
        )

        if response.status_code == 200:
            response = response.json()

            for result in response['classical_search_results'][:RESULTS_LIMIT]:
                await update.message.reply_html(
                    REPLY_TEMPLATES['transcriptions'].format(
                        result['medium']['title'],
                        '، '.join([speaker['name'] for speaker in result['speakers']]),
                        result['playlist']['title'],
                        result['content'],
                        "{:0>8}".format(str(timedelta(seconds=result['start_time']))),
                        "{:0>8}".format(str(timedelta(seconds=result['end_time']))),
                        result['link'],
                    ),
                    disable_web_page_preview=True,
                )
        else:
            await update.message.reply_text(COMMAND_MESSAGES['something_went_wrong'])

    async def __hadiths_handler(self, update: Update) -> None:
        await update.message.reply_text(COMMAND_MESSAGES['wait_for_search'])

        response = get(
            self.baheth_api_base_url + self.hadiths_search_endpoint,
            params={
                'token': self.baheth_api_token,
                'query': update.message.text,
            },
            timeout=10,
        )

        if response.status_code == 200:
            response = response.json()

            for hadith in response['semantic_search_results'][:RESULTS_LIMIT]:
                await update.message.reply_html(
                    REPLY_TEMPLATES['hadiths'].format(
                        hadith['book']['title'],
                        hadith.get('isnad', ''),
                        hadith['matn'],
                        hadith['grade'],
                        hadith['breadcrumb'],
                        hadith['link']
                    )[:MESSAGE_LIMIT],
                    disable_web_page_preview=True,
                )
        else:
            await update.message.reply_text(COMMAND_MESSAGES['something_went_wrong'])


    async def __shamela_handler(self, update: Update) -> None:
        await update.message.reply_text(COMMAND_MESSAGES['wait_for_search'])

        response = get(
            self.baheth_api_base_url + self.shamela_search_endpoint,
            params={
                'token': self.baheth_api_token,
                'query': update.message.text,
            },
            timeout=10,
        )

        if response.status_code == 200:
            response = response.json()

            for result in response['semantic_search_results'][:RESULTS_LIMIT]:
                await update.message.reply_html(
                    REPLY_TEMPLATES['shamela'].format(
                        result['book']['title'],
                        '، '.join([speaker['name'] for speaker in result['authors']]),
                        f"الصفحة {result['page']} من المجلد {result['volume']}" if 'volume' in result else f"الصفحة {result['page']}",
                        result['preview'],
                        result['link'],
                    ),
                    disable_web_page_preview=True,
                )
        else:
            await update.message.reply_text(COMMAND_MESSAGES['something_went_wrong'])
