import re
import string
import unicodedata

import nltk


NORM_TABLE = str.maketrans('“”‘’—–`', '""\'\'--\'')
_en_punkt_sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
_tweet_tokenizer = nltk.tokenize.casual.TweetTokenizer(
    preserve_case=False, reduce_len=True)
_tweet_case_sensitive_tokenizer = nltk.tokenize.casual.TweetTokenizer(
    preserve_case=True, reduce_len=True)


def to_trigrams(words):
    for trigram in nltk.trigrams(words, pad_left=True, pad_right=True):
        yield trigram


def sentence_tokenize(text):
    text = unicodedata.normalize('NFKD', text).translate(NORM_TABLE)

    return tuple(_en_punkt_sentence_tokenizer.tokenize(text))


def prepare_tokens(sentence, lower_case=True):
    if lower_case:
        tokenizer = _tweet_tokenizer
    else:
        tokenizer = _tweet_case_sensitive_tokenizer

    words = tokenizer.tokenize(sentence)

    for index, word in enumerate(words):
        if len(word) == 1 and 0x1f300 <= ord(word) <= 0x1f5ff:
            # Keep emoji
            yield word
        elif len(word) == 1 and word in string.punctuation:
            # Ignore stray symbols which lost meaning by themselves
            if index == len(words) - 1 and word in '.?!':
                # Emit only one final punctuation mark
                yield word
        else:
            # Ignore anything that isn't words or typical English-like text
            match = re.match(r'([!-~]+)', word)

            if match:
                yield match.group(1).strip('-')
