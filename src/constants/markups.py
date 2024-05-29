from telegram import InlineKeyboardButton, InlineKeyboardMarkup


BACK_TO_LIST_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('قائمة الأوامر', callback_data='back_to_list'),
        ],
    ],
)

COMMANDS_MARKUP = InlineKeyboardMarkup(
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

SHOW_MORE_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton('قائمة الأوامر', callback_data='back_to_list'),
            InlineKeyboardButton('عرض المزيد', callback_data='show_more'),
        ],
    ],
)
