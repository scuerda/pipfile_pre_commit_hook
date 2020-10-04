#!/usr/bin/env python

"""Tests for `pipfile_pre_commit_hook` package."""

import pytest
from typing import List

from pipfile_pre_commit_hook.pipfile_pre_commit_hook import check_files

def make_tmp_files(tmp_path, files) -> List[str]:
    full_paths = []
    full_tmp_path = tmp_path
    for f in files:
        if '/' in f:
            parts = f.split('/')
            f = parts[-1]
            full_tmp_path = tmp_path
            for sub_dir in parts[:-1]:
                full_tmp_path = full_tmp_path / sub_dir
                if not full_tmp_path.exists():
                    full_tmp_path.mkdir()
        p = full_tmp_path / f
        p.touch()
        full_paths.append(str(p))
    return full_paths


@pytest.fixture
def good_staged_files(tmp_path):
    staged_files = ['Pipfile', 'Pipfile.lock']
    return make_tmp_files(tmp_path, staged_files)


@pytest.fixture
def bad_staged_files(tmp_path):
    staged_files = ['Pipfile']
    return make_tmp_files(tmp_path, staged_files)


@pytest.fixture
def staged_files_bad_timestamps(tmp_path):
    staged_files = ['Pipfile.lock', 'Pipfile']
    return make_tmp_files(tmp_path, staged_files)


@pytest.fixture
def bad_staged_files_with_subdir(tmp_path):
    staged_files = ['Pipfile', 'Pipfile.lock', 'subdir/Pipfile']
    return make_tmp_files(tmp_path, staged_files)


@pytest.fixture
def good_staged_files_with_subdir(tmp_path):
    staged_files = [
        'Pipfile', 'Pipfile.lock', 'subdir/Pipfile', 'subdir/Pipfile.lock'
    ]
    return make_tmp_files(tmp_path, staged_files)


def test_staged_pipfile_without_lock_fails(bad_staged_files):
    assert check_files(bad_staged_files) == 1


def test_staged_pipfile_with_lock_file_succeeds(good_staged_files):
    assert check_files(good_staged_files) == 0


def test_staged_files_with_out_of_date_lock_fails(staged_files_bad_timestamps):
    assert check_files(staged_files_bad_timestamps) == 1


def test_subdir_with_missing_lock_fails(bad_staged_files_with_subdir):
    assert check_files(bad_staged_files_with_subdir) == 1


def test_subdir_with_lock_fails(good_staged_files_with_subdir):
    assert check_files(good_staged_files_with_subdir) == 0
