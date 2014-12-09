import gzip
import io
import json
import logging
import os.path
import random
import tarfile
import zipfile
import bz2
import sys


_logger = logging.getLogger(__name__)


class UnsupportedArchiveError(OSError):
    pass


def iter_archive(filename, member_file=None, sample=None):
    _logger.info('Loading %s.', filename)

    extension = os.path.splitext(filename)[-1]

    if extension == '.zip':
        archive_file = zipfile.ZipFile(filename)

        for info in archive_file.infolist():
            if sample and random.random() > sample:
                continue

            member_file = archive_file.open(info)

            try:
                for line in iter_archive(info.filename, member_file):
                    yield line
            except UnsupportedArchiveError:
                pass

            member_file.close()

        archive_file.close()

    elif extension == '.tar':
        archive_file = tarfile.TarFile(filename)

        for info in archive_file.getmembers():
            if not info.isfile():
                continue

            if sample and random.random() > sample:
                continue

            member_file = archive_file.extractfile(info)

            try:
                for line in iter_archive(info.name, member_file):
                    yield line
            except UnsupportedArchiveError:
                pass

            member_file.close()

        archive_file.close()

    elif extension == '.gzip':
        if member_file:
            archive_file = gzip.GzipFile(member_file)
        else:
            archive_file = gzip.GzipFile(filename)

        archive_file = io.TextIOWrapper(archive_file, encoding='utf-8')

        for line in archive_file:
            yield line

        archive_file.close()

    elif extension == '.bz2':
        if member_file:
            if sys.version_info < (3, 3):
                # FIXME: write a better backport wrapper for Py 3.2
                archive_file = io.BytesIO(bz2.decompress(member_file.read()))
            else:
                archive_file = bz2.BZ2File(member_file)
        else:
            archive_file = bz2.BZ2File(filename)

        archive_file = io.TextIOWrapper(archive_file, encoding='utf-8')

        for line in archive_file:
            yield line

        archive_file.close()

    else:
        raise UnsupportedArchiveError('Unsupported archive file {}.'
                                      .format(repr(extension)))


def iter_archive_dir(dir_path):
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = sorted(dirs)

        for name in sorted(files):
            filename = os.path.join(root, name)

            try:
                lines = iter_archive(filename)

                for line in lines:
                    yield line

            except UnsupportedArchiveError:
                continue


def iter_archive_dir_json(dir_path):
    for line in iter_archive_dir(dir_path):
        yield json.loads(line)


def sample_from(items, sample=0.5):
    for item in items:
        if random.random() <= sample:
            yield item


def group(items, size=1000):
    group_list = []

    for item in items:
        group_list.append(item)

        if len(group_list) >= size:
            yield group_list
            del group_list[:]

    yield group_list
