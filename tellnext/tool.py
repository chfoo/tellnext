import argparse
import logging
import random
import sys

import tellnext.store
import tellnext.model
import tellnext.training
import tellnext.token
import tellnext.generator
import tellnext.util


_logger = logging.getLogger(__name__)


def main():
    arg_parser = argparse.ArgumentParser()
    sub_parser = arg_parser.add_subparsers()
    arg_parser.add_argument('--database', default=':memory:')
    arg_parser.add_argument('--seed', default=None, type=int)

    train_parser = sub_parser.add_parser('train')
    train_parser.add_argument('file', nargs='+', type=argparse.FileType())
    train_parser.add_argument('--limit-model', default=100000)
    train_parser.add_argument('--keep-case', action='store_true')
    train_parser.set_defaults(func=train_by_plain_text)

    train_by_twitter_parser = sub_parser.add_parser('train-twitter')
    train_by_twitter_parser.add_argument('path', nargs='+')
    train_by_twitter_parser.add_argument('--sample', default=0.3, type=float)
    train_by_twitter_parser.add_argument('--limit-model', default=100000)
    train_by_twitter_parser.set_defaults(func=train_by_twitter)

    generate_parser = sub_parser.add_parser('generate')
    generate_parser.add_argument('--lines', default=1, type=int)
    generate_parser.add_argument('--seed-word')
    generate_parser.add_argument('--no-auto-punctuation', action='store_true')
    generate_parser.set_defaults(func=generate)

    next_word_parser = sub_parser.add_parser('next')
    next_word_parser.add_argument('word1')
    next_word_parser.add_argument('word2', nargs='?')
    next_word_parser.set_defaults(func=next_word)

    args = arg_parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.seed:
        random.seed(args.seed)

    if not hasattr(args, 'func'):
        arg_parser.print_usage()
        sys.exit(1)

    store = tellnext.store.SQLiteStore(path=args.database)
    model = tellnext.model.MarkovModel(store=store)

    args.func(args, model)


def train_by_twitter(args, model):
    for path in args.path:
        lines = tellnext.training.from_twitter_dump(path, sample=args.sample)

        train(args, model, lines)


def train_by_plain_text(args, model):
    for file in args.file:
        train(args, model, file, not args.keep_case)


def train(args, model, lines, lower_case=True):
    count = 0

    trigrams = tellnext.training.process_trigrams(lines, lower_case=lower_case)

    for index, trigrams_group in enumerate(tellnext.util.group(trigrams, size=10000)):
        model.train(trigrams_group)

        count += len(trigrams_group)
        _logger.info('Processed %d trigrams', count)

        if index % 100 == 0 and args.limit_model and \
                model.store.count() > args.limit_model * 2:
            model.store.trim(args.limit_model)

    model.store.trim(args.limit_model)


def generate(args, model):
    generator = tellnext.generator.Generator(model)

    if args.seed_word:
        words = args.seed_word.split()

        if len(words) == 1:
            word_1 = None
            word_2 = words[0]
        elif len(words) == 2:
            word_1, word_2 = words
        else:
            raise Exception('Too many seed words. Max 2.')

    else:
        word_1 = None
        word_2 = None

    for dummy in range(args.lines):
        line = generator.generate_sentence(
            word_1, word_2, final_punctuation=not args.no_auto_punctuation)
        print(line)


def next_word(args, model):
    if args.word2:
        word_1 = args.word1
        word_2 = args.word2
    else:
        word_1 = None
        word_2 = args.word1

    trigram_model = model.get_trigram_model(word_1, word_2)

    for word, score in trigram_model.most_common():
        print(word, score)
