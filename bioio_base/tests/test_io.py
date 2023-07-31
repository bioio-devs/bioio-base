#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib

import pytest

from bioio_base.io import pathlike_to_fs


@pytest.mark.parametrize(
    "enforce_exists",
    [True, False],
)
def test_pathlike_to_fs(enforce_exists: bool, sample_text_file: pathlib.Path) -> None:
    pathlike_to_fs(sample_text_file, enforce_exists, fs_kwargs=dict(anon=True))


@pytest.mark.parametrize(
    "enforce_exists",
    [
        pytest.param(
            True,
            marks=pytest.mark.xfail(raises=FileNotFoundError),
        ),
        (False),
    ],
)
def test_pathlib_to_fs_with_missing_file(
    enforce_exists: bool, tmp_path: pathlib.Path
) -> None:
    uri = tmp_path / "missing-file.txt"

    pathlike_to_fs(uri, enforce_exists, fs_kwargs=dict(anon=True))
