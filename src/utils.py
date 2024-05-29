import re


def remove_html_tags(text: str) -> str:
    return re.compile(r'<.*?>').sub('', text)
