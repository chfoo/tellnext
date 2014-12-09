import collections
import random

from tellnext.store import SQLiteStore


class TrigramModel(collections.Counter):
    def choice(self):
        return random.choice(tuple(self.elements()))


class MarkovModel(object):
    def __init__(self, store=None):
        self.store = store or SQLiteStore(':memory:')

    def train(self, trigrams):
        self.store.add_many(trigrams)

    def get_trigram_model(self, word_1, word_2):
        return TrigramModel(self.store.get_trigram_values(word_1, word_2))

    def next_trigram(self, word_1, word_2):
        return (
            word_1, word_2,
            self.get_trigram_model(word_1, word_2).choice()
        )
