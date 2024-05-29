from telegram.ext import CallbackQueryHandler, ApplicationBuilder, CommandHandler, MessageHandler, filters

from constants import TELEGRAM_BOT_TOKEN

from handlers import (
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
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start_handler))
    app.add_handler(CommandHandler('tafrigh', tafrigh_handler))
    app.add_handler(CommandHandler('transcriptions', transcriptions_handler))
    app.add_handler(CommandHandler('hadiths_semantic', hadiths_semantic_handler))
    app.add_handler(CommandHandler('shamela_semantic', shamela_semantic_handler))
    app.add_handler(CommandHandler('hadiths_classical', hadiths_classical_handler))
    app.add_handler(CommandHandler('shamela_classical', shamela_classical_handler))

    app.add_handler(MessageHandler(filters.TEXT, text_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == '__main__':
    main()
