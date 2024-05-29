from functools import partial

from telegram import Update
from telegram.ext import ContextTypes

from constants import (
    ADMIN_USER_IDS,

    COMMAND_MESSAGES,

    BACK_TO_LIST_MARKUP,
    COMMANDS_MARKUP,
    SHOW_MORE_MARKUP,
)

from processors import (
    tafrigh_processor,
    transcriptions_processor,
    hadiths_processor,
    shamela_semantic_processor,
    shamela_classical_processor,
)


async def enable_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id in ADMIN_USER_IDS:
        context.bot_data['enabled'] = True

        await update.message.reply_text(COMMAND_MESSAGES['bot_enabled_successfully'], reply_markup=BACK_TO_LIST_MARKUP)


async def disable_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.from_user.id in ADMIN_USER_IDS:
        context.bot_data['enabled'] = False

        await update.message.reply_text(COMMAND_MESSAGES['bot_disabled_successfully'], reply_markup=BACK_TO_LIST_MARKUP)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.bot_data['enabled']:
        await update.message.reply_text(COMMAND_MESSAGES['bot_is_not_enabled'], reply_markup=BACK_TO_LIST_MARKUP)
        return

    await update.message.reply_html(COMMAND_MESSAGES['start'], reply_markup=COMMANDS_MARKUP)


async def tafrigh_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.bot_data['enabled']:
        await update.message.reply_text(COMMAND_MESSAGES['bot_is_not_enabled'], reply_markup=BACK_TO_LIST_MARKUP)
        return

    await command_reply_handler(update, context, 'tafrigh')


async def transcriptions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.bot_data['enabled']:
        await update.message.reply_text(COMMAND_MESSAGES['bot_is_not_enabled'], reply_markup=BACK_TO_LIST_MARKUP)
        return

    await command_reply_handler(update, context, 'transcriptions')


async def hadiths_semantic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.bot_data['enabled']:
        await update.message.reply_text(COMMAND_MESSAGES['bot_is_not_enabled'], reply_markup=BACK_TO_LIST_MARKUP)
        return

    await command_reply_handler(update, context, 'hadiths_semantic')


async def shamela_semantic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.bot_data['enabled']:
        await update.message.reply_text(COMMAND_MESSAGES['bot_is_not_enabled'], reply_markup=BACK_TO_LIST_MARKUP)
        return

    await command_reply_handler(update, context, 'shamela_semantic')


async def hadiths_classical_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.bot_data['enabled']:
        await update.message.reply_text(COMMAND_MESSAGES['bot_is_not_enabled'], reply_markup=BACK_TO_LIST_MARKUP)
        return

    await command_reply_handler(update, context, 'hadiths_classical')


async def shamela_classical_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.bot_data['enabled']:
        await update.message.reply_text(COMMAND_MESSAGES['bot_is_not_enabled'], reply_markup=BACK_TO_LIST_MARKUP)
        return

    await command_reply_handler(update, context, 'shamela_classical')


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.bot_data['enabled']:
        await update.message.reply_text(COMMAND_MESSAGES['bot_is_not_enabled'], reply_markup=BACK_TO_LIST_MARKUP)
        return

    await commands_handler(update, context, show_more_button=True)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if not context.bot_data['enabled']:
        await context.bot.send_message(
            chat_id=query.from_user.id,
            text=COMMAND_MESSAGES['bot_is_not_enabled'],
            reply_markup=BACK_TO_LIST_MARKUP,
        )
        return

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    if query.data == 'back_to_list':
        await query.edit_message_text(COMMAND_MESSAGES['start'], reply_markup=COMMANDS_MARKUP, parse_mode='HTML')
    elif query.data == 'show_more':
        await commands_handler(
            update,
            context,
            show_more_button=True,
            show_more_results=True,
            user_id=query.from_user.id,
        )
    else:
        context.user_data['command'] = query.data

        await query.edit_message_text(COMMAND_MESSAGES[query.data], reply_markup=BACK_TO_LIST_MARKUP, parse_mode='HTML')


async def command_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str) -> None:
    context.user_data['command'] = command

    await update.message.reply_html(COMMAND_MESSAGES[command], reply_markup=BACK_TO_LIST_MARKUP)


async def commands_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    show_more_button: bool=False,
    show_more_results: bool=False,
    user_id: int=-1,
) -> None:
    if user_id != -1:
        reply_method = partial(context.bot.send_message, chat_id=user_id)
    else:
        reply_method = update.message.reply_text

    show_commands_list = True

    if (command := context.user_data.get('command', None)):
        if show_more_results:
            context.user_data['results_start'] = context.user_data['results_start'] + 5
        else:
            context.user_data['results_start'] = 0
            context.user_data['message'] = update.message.text

        if command in [
            'transcriptions',
            'hadiths_semantic',
            'shamela_semantic',
            'hadiths_classical',
            'shamela_classical',
        ]:
            if show_more_results:
                await reply_method(text=COMMAND_MESSAGES['getting_more_results'])
            else:
                await reply_method(text=COMMAND_MESSAGES['wait_for_search'])

        match command:
            case 'tafrigh':
                show_more_button = await tafrigh_processor(update)
            case 'transcriptions':
                show_more_button = await transcriptions_processor(context, reply_method)
            case 'hadiths_semantic':
                show_more_button = await hadiths_processor('semantic', context, reply_method)
            case 'shamela_semantic':
                show_more_button = await shamela_semantic_processor(context, reply_method)
            case 'hadiths_classical':
                show_more_button = await hadiths_processor('classical', context, reply_method)
            case 'shamela_classical':
                show_more_button = await shamela_classical_processor(context, reply_method)
            case _:
                await reply_method(text=COMMAND_MESSAGES['no_command_selected'], reply_markup=COMMANDS_MARKUP)
                show_commands_list = False
    else:
        await reply_method(text=COMMAND_MESSAGES['no_command_selected'], reply_markup=COMMANDS_MARKUP)
        show_commands_list = False

    if show_commands_list:
        if show_more_button:
            await reply_method(text=COMMAND_MESSAGES['show_more_continue_or_show_list'], reply_markup=SHOW_MORE_MARKUP)
        else:
            await reply_method(text=COMMAND_MESSAGES['continue_or_show_list'], reply_markup=BACK_TO_LIST_MARKUP)
