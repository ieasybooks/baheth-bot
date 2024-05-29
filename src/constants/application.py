from constants.environment import (
    TELEGRAM_BOT_TOKEN,

    BAHETH_API_BASE_URL,
    MEDIA_ENDPOINT,
    TRANSCRIPTIONS_SEARCH_ENDPOINT,
    HADITHS_SEARCH_ENDPOINT,
    SHAMELA_SEMANTIC_SEARCH_ENDPOINT,
    BAHETH_API_TOKEN,

    TURATH_API_BASE_URL,
    SHAMELA_CLASSICAL_SEARCH_ENDPOINT,
)

from constants.markups import BACK_TO_LIST_MARKUP, COMMANDS_MARKUP, SHOW_MORE_MARKUP

from constants.messages import (
    START_COMMAND_MESSAGE,
    TAFRIGH_COMMAND_MESSAGE,
    TRANSCRIPTIONS_COMMAND_MESSAGE,
    HADITHS_SEMANTIC_COMMAND_MESSAGE,
    SHAMELA_SEMANTIC_COMMAND_MESSAGE,
    HADITHS_CLASSICAL_COMMAND_MESSAGE,
    SHAMELA_CLASSICAL_COMMAND_MESSAGE,
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
    'hadiths_semantic': HADITHS_SEMANTIC_COMMAND_MESSAGE,
    'shamela_semantic': SHAMELA_SEMANTIC_COMMAND_MESSAGE,
    'hadiths_classical': HADITHS_CLASSICAL_COMMAND_MESSAGE,
    'shamela_classical': SHAMELA_CLASSICAL_COMMAND_MESSAGE,
    'no_command_selected': 'اختَر أمرًا من الأوامر الموجودة في القائمة 👇',
    'medium_not_found': 'لم يُعثَر على المادة المطلوبة في قاعدة بيانات باحث 🙁',
    'something_went_wrong': 'حدث خطأ ما، يُرجى المحاولة مرةً أخرى.',
    'wait_for_search': 'جارٍ البحث، إنتظر قليلًا ⌛',
    'continue_or_show_list': 'أكمل باستخدام نفس الأمر أو انتقل إلى قائمة الأوامر 👇',
    'show_more_continue_or_show_list': 'اعرض المزيد من النتائج أو أكمل باستخدام نفس الأمر أو انتقل إلى قائمة الأوامر 👇',
    'getting_more_results': 'جارٍ جلب المزيد من النتائج ⌛',
}

HADITH_MATN_LIMIT = 3500

REPLY_TEMPLATES = {
    'tafrigh': TAFRIGH_REPLY_TEMPLATE,
    'transcriptions': TRANSCRIPTIONS_REPLY_TEMPLATE,
    'hadiths': HADITHS_REPLY_TEMPLATE,
    'shamela': SHAMELA_REPLY_TEMPLATE,
}

RESULTS_LIMIT = 5
