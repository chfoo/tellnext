import re
import unicodedata

import langdetect
from langdetect.lang_detect_exception import LangDetectException

import tellnext.util
import tellnext.token


def from_twitter_dump(dir_path, sample=None):
    docs = tellnext.util.iter_archive_dir_json(dir_path)

    if sample:
        docs = tellnext.util.sample_from(docs, sample)

    for doc in docs:
        line = filter_twitter_text(doc)

        if line:
            yield line


def filter_twitter_text(doc):
    try:
        text = doc['text']
    except KeyError:
        return

    if has_twitter_stop_words(text):
        return

    try:
        profile_description = doc['user']['description'] or ''
    except KeyError:
        return

    if not is_english(profile_description) or not is_english(text):
        return

    return text


def has_twitter_stop_words(text):
    if re.search(r'https?://|#|@|&[a-z]+;', text):
        # links, hashtags, @-reply, and HTML entities
        return True


def is_english(text):
    if not only_roman_chars(text):
        return False

    try:
        stats = langdetect.detect_langs(text)
    except LangDetectException:
        return False

    if any(stats.lang == 'en' for stats in stats):
        return True


_latin_letters = {}


def is_latin(char):
    # http://stackoverflow.com/a/3308844/1524507
    try:
        return _latin_letters[char]
    except KeyError:
        return _latin_letters.setdefault(
            char, 'LATIN' in unicodedata.name(char))


def only_roman_chars(text):
    # http://stackoverflow.com/a/3308844/1524507
    return all(is_latin(char) for char in text if char.isalpha())


def process_trigrams(lines, lower_case=True):
    for line in lines:
        sentences = tellnext.token.sentence_tokenize(line)

        for sentence in sentences:
            words = tellnext.token.prepare_tokens(sentence,
                                                  lower_case=lower_case)

            for trigram in tellnext.token.to_trigrams(words):
                yield trigram
