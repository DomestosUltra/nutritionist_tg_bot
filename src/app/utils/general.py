import re
import markdown
from bs4 import BeautifulSoup, NavigableString

# def mark2html(markdown: str) -> str:
#     # Обработка блоков кода
#     code_blocks = []
#     def replace_code_block(match):
#         lang = match.group(1) or ''
#         code = match.group(2)
#         placeholder = f"{{CODE\_BLOCK\_{len(code_blocks)}}}"
#         code_blocks.append((lang, code))
#         return placeholder
#     code_pattern = r"```([a-z]*)?\n([\s\S]+?)\n```"
#     markdown = re.sub(code_pattern, replace_code_block, markdown, flags=re.MULTILINE)

#     # Функции замены для экранирования текста
#     def bold_replace(match):
#         return f"<b>{html.escape(match.group(1))}</b>"

#     def italic_replace(match):
#         return f"<i>{html.escape(match.group(1))}</i>"

#     def strikethrough_replace(match):
#         return f"<s>{html.escape(match.group(1))}</s>"

#     def spoiler_replace(match):
#         return f'<span class="tg-spoiler">{html.escape(match.group(1))}</span>'

#     def code_replace(match):
#         return f"<code>{html.escape(match.group(1))}</code>"

#     def link_replace(match):
#         text = html.escape(match.group(1))
#         url = match.group(2)
#         return f'<a href="{url}">{text}</a>'

#     # Преобразование поддерживаемого Markdown в HTML
#     markdown = re.sub(r"\*\*(.*?)\*\*", bold_replace, markdown)  # Жирный текст (**text**)
#     markdown = re.sub(r"__(.*?)__", bold_replace, markdown)      # Жирный текст (__text__)
#     markdown = re.sub(r"\*(.*?)\*", italic_replace, markdown)    # Наклонный текст (*text*)
#     markdown = re.sub(r"_(.*?)_", italic_replace, markdown)      # Наклонный текст (_text_)
#     markdown = re.sub(r"~~(.*?)~~", strikethrough_replace, markdown)  # Перечеркнутый текст (~~text~~)
#     markdown = re.sub(r"\|\|(.*?)\|\|", spoiler_replace, markdown)    # Спойлер (||text||)
#     markdown = re.sub(r"`(.*?)`", code_replace, markdown)        # Моноширинный текст (`text`)
#     markdown = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_replace, markdown)  # Ссылки ([text](url))

#     # Удаление остального Markdown построчно
#     lines = markdown.split('\n')
#     for i, line in enumerate(lines):
#         line = re.sub(r"^#+\s*", "", line)          # Удаление заголовков (# Heading)
#         line = re.sub(r"^\s*[-*]\s+", "", line)     # Удаление ненумерованных списков (- item)
#         line = re.sub(r"^\s*\d+\.\s+", "", line)    # Удаление нумерованных списков (1. item)
#         line = re.sub(r"^>\s*", "", line)           # Удаление цитат (> quote)
#         if re.match(r"^\s*[-*_]{3,}\s*$", line):    # Удаление горизонтальных линий (---)
#             line = ""
#         lines[i] = line
#     markdown = '\n'.join(lines)

#     # Вставка блоков кода
#     for i, (lang, code) in enumerate(code_blocks):
#         placeholder = f"{{CODE_BLOCK_{i}}}"
#         code = html.escape(code)
#         html_code = f'<pre><code class="language-{lang}">{code}</code></pre>' if lang else f'<pre><code>{code}</code></pre>'
#         markdown = markdown.replace(placeholder, html_code)

#     # Удаление дополнительных элементов Markdown
#     markdown = re.sub(r"!\[([^\]]*)\]\([^\)]+\)", r"\1", markdown)  # Удаление изображений, оставляя alt-текст
#     markdown = re.sub(r"<(https?://[^\>]+)>", r"\1", markdown)      # Удаление автоссылок

#     return markdown


import re
import html
from urllib.parse import quote


def markdown_to_html(text):
    # Обработка многострочных блоков кода
    text = re.sub(
        r"```(.*?)```",
        lambda m: f"<pre><code>{html.escape(m.group(1))}</code></pre>",
        text,
        flags=re.DOTALL,
    )

    # Обработка моноширинных блоков кода
    text = re.sub(
        r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", text
    )

    # Обработка подчеркивания
    text = re.sub(r"__(.+?)__", r"<u>\1</u>", text)

    # Обработка жирного текста
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)

    # Обработка курсива
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)

    # Обработка зачеркивания
    text = re.sub(r"~~(.+?)~~", r"<s>\1</s>", text)

    # Обработка ссылок
    text = re.sub(
        r"\[(.+?)\]\((.*?)\)",
        lambda m: f'<a href="{quote(m.group(2), safe=":/?&=").replace("&", "&amp;")}">{html.escape(m.group(1))}</a>',
        text,
    )

    parts = re.split(r"(<[^>]+>)", text)
    for i in range(len(parts)):
        if not re.match(r"<[^>]+>$", parts[i]):
            parts[i] = html.escape(parts[i])
    text = "".join(parts)

    return text


import markdown


def mark2html(md_text):
    return markdown.markdown(md_text)


def convert_to_allowed_tags(input_text: str) -> str:
    # Список разрешенных тегов
    allowed_tags = {
        "b",
        "strong",
        "i",
        "em",
        "code",
        "s",
        "strike",
        "del",
        "u",
        "pre",
    }

    # Преобразование Markdown в HTML
    html = markdown.markdown(input_text, extensions=["extra"])

    # Парсинг HTML
    soup = BeautifulSoup(html, "html.parser")

    # Функция проверки разрешенных тегов
    def is_allowed(tag):
        return tag.name in allowed_tags or (
            tag.name == "pre" and tag.has_attr("language")
        )

    # Рекурсивная функция для фильтрации тегов
    def filter_tags(element):
        if isinstance(element, NavigableString):
            # Если это текст, возвращаем его как есть
            return element
        if is_allowed(element):
            # Сохраняем разрешенный тег и обрабатываем его содержимое
            element.attrs = {
                k: v for k, v in element.attrs.items() if k == "language"
            }  # Оставляем только атрибут language
            new_contents = [filter_tags(child) for child in element.contents]
            element.clear()
            for content in new_contents:
                element.append(content)
            return element
        else:
            # Удаляем тег, возвращая только его содержимое как текст
            return "".join(
                str(filter_tags(child)) for child in element.contents
            )

    # Применяем фильтрацию ко всему документу
    filtered_html = filter_tags(soup)

    # Возвращаем результат как строку
    return str(filtered_html)
