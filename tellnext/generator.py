

class Generator(object):
    def __init__(self, model):
        self.model = model

    def generate_sentence(self, word_1=None, word_2=None, max_words=30,
                          final_punctuation=True):
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

            if words and word_3 not in '.!?':
                words.append(' ')

            words.append(word_3)

            word_1 = word_2
            word_2 = word_3

        if final_punctuation and words and words[-1][-1] not in '.!?':
            words.append('.')

        return ''.join(words)
