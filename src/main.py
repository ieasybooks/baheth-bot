from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from constants import TELEGRAM_BOT_TOKEN

from handlers import (
    enable_bot_handler,
    disable_bot_handler,
    start_handler,
    tafrigh_handler,
    transcriptions_handler,
    hadiths_semantic_handler,
    shamela_semantic_handler,
    hadiths_classical_handler,
    shamela_classical_handler,
    text_handler,
    button_handler,
)


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler('enable_bot', enable_bot_handler))
    application.add_handler(CommandHandler('disable_bot', disable_bot_handler))

    application.add_handler(CommandHandler('start', start_handler))
    application.add_handler(CommandHandler('tafrigh', tafrigh_handler))
    application.add_handler(CommandHandler('transcriptions', transcriptions_handler))
    application.add_handler(CommandHandler('hadiths_semantic', hadiths_semantic_handler))
    application.add_handler(CommandHandler('shamela_semantic', shamela_semantic_handler))
    application.add_handler(CommandHandler('hadiths_classical', hadiths_classical_handler))
    application.add_handler(CommandHandler('shamela_classical', shamela_classical_handler))

    application.add_handler(MessageHandler(filters.TEXT, text_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()


async def post_init(application: Application) -> None:
    application.bot_data['enabled'] = True


if __name__ == '__main__':
    main()
