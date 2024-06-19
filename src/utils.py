import re

from urllib.parse import parse_qs, urlparse


def remove_html_tags(text: str) -> str:
  return re.compile(r'<.*?>').sub('', text)


def video_id_from_link(link: str) -> str:
  if 'youtu.be/' in link:
    return link.split('youtu.be/')[1].split('?')[0]
  else:
    return parse_qs(urlparse(link).query)['v'][0]
