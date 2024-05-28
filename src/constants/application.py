from constants.messages import (
    START_COMMAND_MESSAGE,
    TAFRIGH_COMMAND_MESSAGE,
    TRANSCRIPTIONS_COMMAND_MESSAGE,
    HADITHS_COMMAND_MESSAGE,
    SHAMELA_COMMAND_MESSAGE,
)

from constants.templates import (
    TAFRIGH_REPLY_TEMPLATE,
    TRANSCRIPTIONS_REPLY_TEMPLATE,
    HADITHS_REPLY_TEMPLATE,
    SHAMELA_REPLY_TEMPLATE,
)


COMMAND_MESSAGES = {
    'start': START_COMMAND_MESSAGE,
    'tafrigh': TAFRIGH_COMMAND_MESSAGE,
    'transcriptions': TRANSCRIPTIONS_COMMAND_MESSAGE,
    'hadiths': HADITHS_COMMAND_MESSAGE,
    'shamela': SHAMELA_COMMAND_MESSAGE,
    'no_command_selected': 'اختَر أمرًا من الأوامر الموجودة في القائمة 👇',
    'medium_not_found': 'لم يُعثَر على المادة المطلوبة في قاعدة بيانات باحث 🙁',
    'something_went_wrong': 'حدث خطأ ما، يُرجى المحاولة لاحقا.',
    'wait_for_search': 'جارٍ البحث، إنتظر قليلًا ⌛',
}

MESSAGE_LIMIT = 4096

REPLY_TEMPLATES = {
    'tafrigh': TAFRIGH_REPLY_TEMPLATE,
    'transcriptions': TRANSCRIPTIONS_REPLY_TEMPLATE,
    'hadiths': HADITHS_REPLY_TEMPLATE,
    'shamela': SHAMELA_REPLY_TEMPLATE,
}

RESULTS_LIMIT = 5
