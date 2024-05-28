import json
import re

from datetime import timedelta
from typing import Self

from requests import get
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

from constants import COMMAND_MESSAGES, MESSAGE_LIMIT, REPLY_TEMPLATES, RESULTS_LIMIT


class Bot:
    def __init__(
        self,

        telegram_bot_token: str,

        baheth_api_base_url: str,
        media_endpoint: str,
        transcriptions_search_endpoint: str,
        hadiths_search_endpoint: str,
        shamela_semantic_search_endpoint: str,
        baheth_api_token: str,

        turath_api_base_url: str,
        shamela_classical_search_endpoint: str,
    ) -> Self:
        super().__init__()

        self.users = dict()

        self.telegram_bot_token = telegram_bot_token

        self.baheth_api_base_url = baheth_api_base_url
        self.media_endpoint = media_endpoint
        self.transcriptions_search_endpoint = transcriptions_search_endpoint
        self.hadiths_search_endpoint = hadiths_search_endpoint
        self.shamela_semantic_search_endpoint = shamela_semantic_search_endpoint
        self.baheth_api_token = baheth_api_token

        self.turath_api_base_url = turath_api_base_url
        self.shamela_classical_search_endpoint = shamela_classical_search_endpoint

        self.commands_list = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('البحث في التفريغات بالنص', callback_data='transcriptions'),
                    InlineKeyboardButton('طلب تفريغ مادة', callback_data='tafrigh'),
                ],
                [
                    InlineKeyboardButton('البحث في الشاملة بالمعنى', callback_data='shamela_semantic'),
                    InlineKeyboardButton('البحث في الأحاديث بالمعنى', callback_data='hadiths_semantic'),
                ],
                [
                    InlineKeyboardButton('البحث في الشاملة بالنص', callback_data='shamela_classical'),
                    InlineKeyboardButton('البحث في الاحاديث بالنص', callback_data='hadiths_classical'),
                ],
            ],
        )

        self.back_to_list = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('قائمة الأوامر', callback_data='back_to_list'),
                ],
            ],
        )


    def run(self) -> None:
        app = ApplicationBuilder().token(self.telegram_bot_token).build()

        app.add_handler(CommandHandler('start', self.start))
        app.add_handler(CommandHandler('tafrigh', self.tafrigh))
        app.add_handler(CommandHandler('transcriptions', self.transcriptions))
        app.add_handler(CommandHandler('hadiths_semantic', self.hadiths_semantic))
        app.add_handler(CommandHandler('shamela_semantic', self.shamela_semantic))
        app.add_handler(CommandHandler('hadiths_classical', self.hadiths_classical))
        app.add_handler(CommandHandler('shamela_classical', self.shamela_classical))

        app.add_handler(MessageHandler(filters.TEXT, self.text_handler))
        app.add_handler(CallbackQueryHandler(self.button))

        app.run_polling()


    async def start(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        self.users[update.message.from_user.id] = 'start'
        await update.message.reply_html(COMMAND_MESSAGES['start'], reply_markup=self.commands_list)


    async def tafrigh(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'tafrigh')


    async def transcriptions(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'transcriptions')


    async def hadiths_semantic(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'hadiths_semantic')


    async def shamela_semantic(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'shamela_semantic')


    async def hadiths_classical(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'hadiths_classical')


    async def shamela_classical(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        await self.__command_reply_handler(update, 'shamela_classical')


    async def button(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
        await query.answer()

        self.users[query.from_user.id] = query.data

        if query.data == 'back_to_list':
            await query.edit_message_text(COMMAND_MESSAGES['start'], reply_markup=self.commands_list, parse_mode='HTML')
        else:
            await query.edit_message_text(
                COMMAND_MESSAGES[query.data],
                reply_markup=self.back_to_list,
                parse_mode='HTML',
            )


    async def text_handler(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.message.from_user.id

        show_commands_list = True

        if (command := self.users.get(user_id)):
            match command:
                case 'tafrigh':
                    await self.__tafrigh_handler(update)
                case 'transcriptions':
                    await self.__transcriptions_handler(update)
                case 'hadiths_semantic':
                    await self.__hadiths_handler(update, 'semantic')
                case 'shamela_semantic':
                    await self.__shamela_semantic_handler(update)
                case 'hadiths_classical':
                    await self.__hadiths_handler(update, 'classical')
                case 'shamela_classical':
                    await self.__shamela_classical_handler(update)
                case _:
                    await update.message.reply_text(
                        COMMAND_MESSAGES['no_command_selected'],
                        reply_markup=self.commands_list,
                    )
                    show_commands_list = False
        else:
            await update.message.reply_text(COMMAND_MESSAGES['no_command_selected'], reply_markup=self.commands_list)
            show_commands_list = False

        if show_commands_list:
            await update.message.reply_text(COMMAND_MESSAGES['continue_or_show_list'], reply_markup=self.back_to_list)


    async def __command_reply_handler(self, update: Update, command: str) -> None:
        self.users[update.message.from_user.id] = command

        await update.message.reply_html(COMMAND_MESSAGES[command], reply_markup=self.back_to_list)


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

    async def __hadiths_handler(self, update: Update, search_type: str) -> None:
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

            for hadith in response[f'{search_type}_search_results'][:RESULTS_LIMIT]:
                await update.message.reply_html(
                    REPLY_TEMPLATES['hadiths'].format(
                        hadith['book']['title'],
                        hadith.get('isnad', ''),
                        hadith['matn'][:MESSAGE_LIMIT],
                        hadith['grade'],
                        hadith['breadcrumb'],
                        hadith['link']
                    ),
                    disable_web_page_preview=True,
                )
        else:
            await update.message.reply_text(COMMAND_MESSAGES['something_went_wrong'])


    async def __shamela_semantic_handler(self, update: Update) -> None:
        await update.message.reply_text(COMMAND_MESSAGES['wait_for_search'])

        response = get(
            self.baheth_api_base_url + self.shamela_semantic_search_endpoint,
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


    async def __shamela_classical_handler(self, update: Update) -> None:
        await update.message.reply_text(COMMAND_MESSAGES['wait_for_search'])

        response = get(
            self.turath_api_base_url + self.shamela_classical_search_endpoint,
            params={
                'q': update.message.text,
                'ver': 3,
                'precision': 2,
            },
            timeout=10,
        )

        if response.status_code == 200:
            response = response.json()

            for result in response['data'][:RESULTS_LIMIT]:
                meta = json.loads(result['meta'])

                text = REPLY_TEMPLATES['shamela'].format(
                    meta['book_name'],
                    meta['author_name'],
                    f"الصفحة {meta['page']} من المجلد {meta['vol']}" if 'vol' in meta else f"الصفحة {meta['page']}",
                    f"{self.remove_html_tags(result['snip'])}...",
                    f"https://app.turath.io/book/{result['book_id']}?page={meta['page_id']}",
                )

                await update.message.reply_html(text, disable_web_page_preview=True)
        else:
            await update.message.reply_text(COMMAND_MESSAGES['something_went_wrong'])


    def remove_html_tags(self, text: str) -> str:
        return re.compile(r'<.*?>').sub('', text)
