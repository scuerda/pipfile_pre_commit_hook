"""Main module."""
import argparse
import pathlib

from datetime import datetime
from typing import Optional
from typing import Sequence


def update_time(filename: str) -> datetime:
    return pathlib.Path(filename).stat().st_mtime


def check_files(
        filenames: Sequence[str]
) -> int:
    """We want to grab all the files in filenames and if we have a
    Pipfile, we want to make sure we have a Pipfile.lock in the same subdir
    in the changed file list"""
    failed = 0
    pipfiles_without_committed_locks = []
    pipfiles_with_old_lockfiles = []
    for f in filenames:
        if f.endswith('.lock'):
            continue
        lock_file = f'{f}.lock'
        if lock_file not in filenames:
            failed = 1
            pipfiles_without_committed_locks.append(f)
        else:
            if update_time(f) > update_time(lock_file):
                failed = 1
                pipfiles_with_old_lockfiles.append((f, lock_file))

    if failed:
        for pipfile in pipfiles_without_committed_locks:
            print(
                f'Pipfile.lock not staged for `{pipfile}`. Please run either '
                f'`pipenv install` or `pipenv sync` to generate an updated '
                f'Pipfile.lock.'
            )
        for pipfile, lockfile in pipfiles_with_old_lockfiles:
            print(
                f'It looks like `{lockfile}` wasn\'t updated after your most '
                f'recent edit to `{pipfile}`. Please run either '
                f'`pipenv install` or `pipenv sync` to generate an updated '
                f'Pipfile.lock.'
            )

    return failed


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filenames', nargs='*',
        help='Filenames pre-commit belives are changed.',
    )
    args = parser.parse_args(argv)

    return check_files(args.filenames)
