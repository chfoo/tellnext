import re


CONTRACTIONS = frozenset((
    ('can', 'not'),
    ('d', "'ye"),
    ('gim', 'me'),
    ('gon', 'na'),
    ('got', 'ta'),
    ('lem', 'me'),
    ('mor', "'n"),
    ('wan', 'na'),
    ("'t", 'is'),
    ("'t", 'was'),
))

ENDING_QUOTES = frozenset((
    "'s",
    "'m",
    "'d",
    "'ll",
    "'re",
    "'ve",
    "n't",
))


class Generator(object):
    def __init__(self, model):
        self.model = model

    def generate_sentence(self, word_1=None, word_2=None, max_words=30):
        assert (not word_1 and not word_2 or
                not word_1 and word_2 or
                word_1 and word_2)

        words = []

        if word_1:
            words.append(word_1)

        if word_2:
            if words:
                words.append(' ')

            words.append(word_2)

        for dummy in range(max_words):
            try:
                trigram = self.model.next_trigram(word_1, word_2)
            except KeyError:
                break

            word_3 = trigram[2]

            if not word_3:
                break

            if words and not re.search(r'[.!?]', word_3):
                if not (
                        (word_2, word_3) in CONTRACTIONS or
                        word_3 in ENDING_QUOTES or
                        word_2 == '``'
                ):
                    words.append(' ')

            words.append(word_3)

            word_1 = word_2
            word_2 = word_3

        if words and words[-1][-1] not in '.!?':
            words.append('.')

        return ''.join(words)
