import json
import os
import random
import time

from datetime import timedelta
from typing import Callable

from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from telegram import Update
from telegram.ext import ContextTypes

from constants import (BAHETH_API_BASE_URL, BAHETH_API_TOKEN, COMMAND_MESSAGES, HADITH_MATN_LIMIT,
                       HADITHS_SEARCH_ENDPOINT, MEDIA_ENDPOINT, REPLY_TEMPLATES, RESULTS_LIMIT,
                       SHAMELA_CLASSICAL_SEARCH_ENDPOINT, SHAMELA_SEMANTIC_SEARCH_ENDPOINT,
                       TRANSCRIPTIONS_SEARCH_ENDPOINT, TURATH_API_BASE_URL)
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
    await try_tafrigh_from_youtube(update)
  elif response.status_code == 200:
    response_json = response.json()

    await update.message.reply_html(
      REPLY_TEMPLATES['tafrigh'].format(
        response_json['title'],
        # '، '.join([speaker['name'] for speaker in response_json['speakers']]),
        # response_json['playlist']['title'],
        response_json['link'],
        response_json['transcription_link'],
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

    response_json = response.json()

    for result in response_json['classical_search_results'][results_start:results_start + RESULTS_LIMIT]:
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

    return results_start + RESULTS_LIMIT < len(response_json['classical_search_results'])

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

    response_json = response.json()

    for hadith in response_json[f'{search_type}_search_results'][results_start:results_start + RESULTS_LIMIT]:
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

    return results_start + RESULTS_LIMIT < len(response_json[f'{search_type}_search_results'])

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

    response_json = response.json()

    for result in response_json['semantic_search_results'][results_start:results_start + RESULTS_LIMIT]:
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

    return results_start + RESULTS_LIMIT < len(response_json['semantic_search_results'])

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

    response_json = response.json()

    for result in response_json['data'][results_start:results_start + RESULTS_LIMIT]:
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

    return results_start + RESULTS_LIMIT < len(response_json['data'])

  await reply_method(text=COMMAND_MESSAGES['something_went_wrong'])

  return False


async def try_tafrigh_from_youtube(update: Update) -> None:
  try:
    video_id = video_id_from_link(update.message.text)

    folder_name = str(random.randint(0, 9_000_000))

    os.mkdir(folder_name)

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_experimental_option('prefs', {'download.default_directory': os.path.abspath(folder_name)})

    browser = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)

    browser.get('https://downsub.com/?url=' + update.message.text)

    WebDriverWait(browser, 10).until(
      EC.element_to_be_clickable((By.XPATH, "//button[starts-with(@data-title, '[TXT] Arabic')]"))
    ).click()

    trials = 0
    while trials < 10 and len(os.listdir(folder_name)) != 1:
      time.sleep(1)
      trials += 1

    browser.close()

    if len(os.listdir(folder_name)) == 1:
      await update.message.reply_text(COMMAND_MESSAGES['transcription_fetched_from_youtube'])

      await update.message.reply_document(
        document=bytes(open(os.path.join(folder_name, os.listdir(folder_name)[0])).read(), 'utf-8'),
        filename=f'{video_id}.txt',
      )
    else:
      await update.message.reply_text(COMMAND_MESSAGES['medium_not_found'])
  except:
    await update.message.reply_text(COMMAND_MESSAGES['medium_not_found'])
  finally:
    os.remove(os.path.join(folder_name, os.listdir(folder_name)[0]))
    os.rmdir(folder_name)
