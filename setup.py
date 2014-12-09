from distutils.core import setup
import os
import re


def get_version():
    path = os.path.join(os.path.dirname(__file__), 'tellnext', '__init__.py')
    with open(path) as in_file:
        text = in_file.read()

        match = re.search(r"__version__ = '([^']+)'", text)

        return match.group(1)


if __name__ == '__main__':
    setup(
         name='tellnext',
         version=get_version(),
         description='Next word prediction using a Markov chain and trigram model.',
         author='Christopher Foo',
         author_email='chris.foo@gmail.com',
         url='https://github.com/chfoo/tellnext',
         packages=['tellnext'],
         install_requires=['nltk', 'langdetect']
    )
