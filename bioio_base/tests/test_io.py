#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib

import pytest

from bioio_base.io import pathlike_to_fs, s3_https_to_s3


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


@pytest.mark.parametrize(
    "uri, expected_uri",
    [
        (
            "https://s3.us-west-2.amazonaws.com/my-bucket/some/key",
            "s3://my-bucket/some/key",
        ),
        (
            "https://s3.amazonaws.com/my-bucket/some/key",
            "s3://my-bucket/some/key",
        ),
        (
            "https://s3.dualstack.us-west-2.amazonaws.com/my-bucket/some/key",
            "s3://my-bucket/some/key",
        ),
        (
            "https://my-bucket.s3.us-west-2.amazonaws.com/some/key",
            "s3://my-bucket/some/key",
        ),
        (
            "https://my.dotted.bucket.s3.amazonaws.com/some/key",
            "s3://my.dotted.bucket/some/key",
        ),
        (
            "http://s3.us-west-2.amazonaws.com/my-bucket/some/key",
            "s3://my-bucket/some/key",
        ),
        (
            "https://s3.us-west-2.amazonaws.com/my-bucket/some/key?versionId=abc",
            "s3://my-bucket/some/key",
        ),
    ],
)
def test_s3_https_to_s3(uri: str, expected_uri: str) -> None:
    assert s3_https_to_s3(uri) == (expected_uri, {"anon": True})


def test_s3_https_to_s3_keeps_given_fs_kwargs() -> None:
    uri = "https://s3.us-west-2.amazonaws.com/my-bucket/key"

    _, fs_kwargs = s3_https_to_s3(uri, {"anon": False, "use_ssl": False})

    assert fs_kwargs == {"anon": False, "use_ssl": False}


@pytest.mark.parametrize(
    "uri",
    [
        "s3://my-bucket/some/key",
        "https://example.org/my-bucket/some/key",
        "https://s3.example.org/my-bucket/some/key",
        "https://example.amazonaws.com/some/key",
        "/local/path/to/image",
        "memory://image",
    ],
)
def test_s3_https_to_s3_leaves_other_uris_alone(uri: str) -> None:
    assert s3_https_to_s3(uri, {"key": "value"}) == (uri, {"key": "value"})


@pytest.mark.parametrize(
    "query",
    ["X-Amz-Signature=abc&X-Amz-Expires=60", "AWSAccessKeyId=id&Signature=abc"],
)
def test_s3_https_to_s3_rejects_presigned_url(query: str) -> None:
    with pytest.raises(ValueError, match="presigned"):
        s3_https_to_s3("https://s3.us-west-2.amazonaws.com/my-bucket/key?" + query)
