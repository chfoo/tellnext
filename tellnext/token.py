import re
import unicodedata

import nltk


NORM_TABLE = str.maketrans('“”‘’—–`', '""\'\'--\'')
_en_punkt_sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
_treeband_word_tokenizer = nltk.TreebankWordTokenizer()


def to_trigrams(words):
    for trigram in nltk.trigrams(words, pad_left=True, pad_right=True,
                                 pad_symbol=None):
        yield trigram


def sentence_tokenize(text):
    text = unicodedata.normalize('NFKD', text).translate(NORM_TABLE)

    return tuple(_en_punkt_sentence_tokenizer.tokenize(text))


def prepare_tokens(sentence):
    def replacement(match):
        return match.group(2)[:2]

    # Strip repeating characters
    sentence = re.sub(r'(.)(\1{2,})', replacement, sentence)

    sentence = sentence.lower()

    words = tuple(rejoin_emoticons(_treeband_word_tokenizer.tokenize(sentence)))

    for index, word in enumerate(words):
        # # Ignore double quotation marks expanded by treeband tokenizer
        # if word in ('``', "''"):
        #     continue

        # Ignore embellishments/emoticons except for a few ASCII ones
        if word in (':d', ':)', ':(', ':p', '-_-', ':x', ':o', ':s', ':c',):
            if word == ':d':
                yield ':D'
            else:
                yield word
        elif len(word) == 1 and 0x1f300 <= ord(word) <= 0x1f5ff:
            # Keep emoji
            yield word
        elif word in ('``', "''"):
            # Ignore treebank quotation marks
            pass
        else:
            # Ignore anything that isn't words
            match = re.match(r'([a-zA-Z0-9\'-]+)', word)

            if match:
                new_word = match.group(1).strip('-')

                if new_word:
                    yield new_word

        if index == len(words) - 1:
            # Emit only one final punctuation mark
            if word and word[-1] in '.?!':
                yield word[-1]


def rejoin_emoticons(words):
    prev_word = None

    for word in words:
        if word == ':':
            prev_word = word
        elif prev_word:
            if len(word) == 1:
                yield '{}{}'.format(prev_word, word)
                prev_word = None
            else:
                yield prev_word
                yield word
                prev_word = None
        else:
            yield word
