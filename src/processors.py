import json

from datetime import timedelta
from typing import Callable

from requests import get
from telegram import Update
from telegram.ext import ContextTypes
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

from constants import (
    COMMAND_MESSAGES,
    HADITH_MATN_LIMIT,
    REPLY_TEMPLATES,
    RESULTS_LIMIT,

    BAHETH_API_BASE_URL,
    MEDIA_ENDPOINT,
    TRANSCRIPTIONS_SEARCH_ENDPOINT,
    HADITHS_SEARCH_ENDPOINT,
    SHAMELA_SEMANTIC_SEARCH_ENDPOINT,
    BAHETH_API_TOKEN,

    TURATH_API_BASE_URL,
    SHAMELA_CLASSICAL_SEARCH_ENDPOINT,
)

from utils import remove_html_tags, video_id_from_link


async def tafrigh_processor(update: Update) -> bool:
    response = get(
        BAHETH_API_BASE_URL + MEDIA_ENDPOINT,
        params={
            'reference_id': update.message.text,
            'reference_type': 'youtube_link',
        },
        timeout=10,
    )

    if response.status_code == 404:
        try:
            video_id = video_id_from_link(update.message.text)
            transcription = YouTubeTranscriptApi.list_transcripts(video_id).find_transcript(['ar']).fetch()

            await update.message.reply_text(COMMAND_MESSAGES['transcription_fetched_from_youtube'])

            await update.message.reply_document(
                document=bytes(TextFormatter().format_transcript(transcription), 'utf-8'),
                filename=f'{video_id}.txt',
            )
        except:
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

    return False


async def transcriptions_processor(context: ContextTypes.DEFAULT_TYPE, reply_method: Callable) -> bool:
    response = get(
        BAHETH_API_BASE_URL + TRANSCRIPTIONS_SEARCH_ENDPOINT,
        params={
            'token': BAHETH_API_TOKEN,
            'query': context.user_data['message'],
        },
        timeout=10,
    )

    if response.status_code == 200:
        results_start = context.user_data['results_start']

        response = response.json()

        for result in response['classical_search_results'][results_start:results_start + RESULTS_LIMIT]:
            await reply_method(
                text=REPLY_TEMPLATES['transcriptions'].format(
                    result['medium']['title'],
                    '، '.join([speaker['name'] for speaker in result['speakers']]),
                    result['playlist']['title'],
                    result['content'],
                    "{:0>8}".format(str(timedelta(seconds=result['start_time']))),
                    "{:0>8}".format(str(timedelta(seconds=result['end_time']))),
                    result['link'],
                ),
                disable_web_page_preview=True,
                parse_mode='HTML',
            )

        return results_start + RESULTS_LIMIT < len(response['classical_search_results'])

    await reply_method(COMMAND_MESSAGES['something_went_wrong'])

    return False


async def hadiths_processor(search_type: str, context: ContextTypes.DEFAULT_TYPE, reply_method: Callable) -> bool:
    response = get(
        BAHETH_API_BASE_URL + HADITHS_SEARCH_ENDPOINT,
        params={
            'token': BAHETH_API_TOKEN,
            'query': context.user_data['message'],
            'search_type': search_type,
        },
        timeout=10,
    )

    if response.status_code == 200:
        results_start = context.user_data['results_start']

        response = response.json()

        for hadith in response[f'{search_type}_search_results'][results_start:results_start + RESULTS_LIMIT]:
            await reply_method(
                text=REPLY_TEMPLATES['hadiths'].format(
                    hadith['book']['title'],
                    hadith.get('isnad', ''),
                    hadith['matn'][:HADITH_MATN_LIMIT],
                    hadith['grade'],
                    hadith['breadcrumb'],
                    hadith['link']
                ),
                disable_web_page_preview=True,
                parse_mode='HTML',
            )

        return results_start + RESULTS_LIMIT < len(response[f'{search_type}_search_results'])

    await reply_method(text=COMMAND_MESSAGES['something_went_wrong'])

    return False


async def shamela_semantic_processor(context: ContextTypes.DEFAULT_TYPE, reply_method: Callable) -> bool:
    response = get(
        BAHETH_API_BASE_URL + SHAMELA_SEMANTIC_SEARCH_ENDPOINT,
        params={
            'token': BAHETH_API_TOKEN,
            'query': context.user_data['message'],
        },
        timeout=10,
    )

    if response.status_code == 200:
        results_start = context.user_data['results_start']

        response = response.json()

        for result in response['semantic_search_results'][results_start:results_start + RESULTS_LIMIT]:
            await reply_method(
                text=REPLY_TEMPLATES['shamela'].format(
                    result['book']['title'],
                    '، '.join([speaker['name'] for speaker in result['authors']]),
                    f"الصفحة {result['page']} من المجلد {result['volume']}" if 'volume' in result else f"الصفحة {result['page']}",
                    result['preview'],
                    result['link'],
                ),
                disable_web_page_preview=True,
                parse_mode='HTML',
            )

        return results_start + RESULTS_LIMIT < len(response['semantic_search_results'])

    await reply_method(text=COMMAND_MESSAGES['something_went_wrong'])

    return False


async def shamela_classical_processor(context: ContextTypes.DEFAULT_TYPE, reply_method: Callable) -> bool:
    response = get(
        TURATH_API_BASE_URL + SHAMELA_CLASSICAL_SEARCH_ENDPOINT,
        params={
            'q': context.user_data['message'],
            'ver': 3,
            'precision': 2,
        },
        timeout=10,
    )

    if response.status_code == 200:
        results_start = context.user_data['results_start']

        response = response.json()

        for result in response['data'][results_start:results_start + RESULTS_LIMIT]:
            meta = json.loads(result['meta'])

            await reply_method(
                text=REPLY_TEMPLATES['shamela'].format(
                    meta['book_name'],
                    meta['author_name'],
                    f"الصفحة {meta['page']} من المجلد {meta['vol']}" if 'vol' in meta else f"الصفحة {meta['page']}",
                    f"{remove_html_tags(result['snip'])}...",
                    f"https://app.turath.io/book/{result['book_id']}?page={meta['page_id']}",
                ),
                disable_web_page_preview=True,
                parse_mode='HTML',
            )

        return results_start + RESULTS_LIMIT < len(response['data'])

    await reply_method(text=COMMAND_MESSAGES['something_went_wrong'])

    return False
