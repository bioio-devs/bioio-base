#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from typing import BinaryIO
from urllib.request import ProxyHandler, build_opener

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
    "filename, url_filename, encoded_filename",
    [
        ("a b=0.tiff", "a b=0.tiff", "a%20b=0.tiff"),
        ("a b=0.tiff", "a%20b=0.tiff", "a%20b=0.tiff"),
        ("a  bcafé.tiff", "a  bcafé.tiff", "a%20%20bcaf%C3%A9.tiff"),
    ],
    ids=["literal-spaces", "encoded-spaces", "multiple-spaces-unicode"],
)
def test_pathlike_to_fs_http_url_path(
    tmp_path: pathlib.Path, filename: str, url_filename: str, encoded_filename: str
) -> None:
    (tmp_path / filename).write_bytes(b"image bytes")
    query = "X-Amz-Signature=f00d&foo=a%2Fb%2B%3D&foo=2"
    targets: list[str] = []

    class Handler(SimpleHTTPRequestHandler):
        def send_head(self) -> BinaryIO | None:
            targets.append(self.path)
            return super().send_head()

    with HTTPServer(("127.0.0.1", 0), partial(Handler, directory=tmp_path)) as server:
        thread = Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05})
        thread.start()
        try:
            origin = f"http://127.0.0.1:{server.server_port}"
            target = f"/{encoded_filename}?{query}"
            fs, path = pathlike_to_fs(f"{origin}/{url_filename}?{query}#view")
            assert path == f"{origin}{target}#view"
            with build_opener(ProxyHandler({})).open(path, timeout=5) as stream:
                assert stream.read() == b"image bytes"
            assert targets == [target]
            assert fs.exists(path)
            with fs.open(path, "rb") as stream:
                assert stream.read() == b"image bytes"
        finally:
            server.shutdown()
            thread.join()


def test_pathlike_to_fs_https_preserves_query_and_fragment() -> None:
    uri = "https://example.invalid/a b%20c\t%23%3F=0.czi?x=%2f&x=+##view?raw"
    _, path = pathlike_to_fs(uri)
    assert (
        path == "https://example.invalid/a%20b%20c%09%23%3F=0.czi?x=%2f&x=+##view?raw"
    )


def test_pathlike_to_fs_preserves_local_path(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "a b#=é%20.tiff"
    path.write_bytes(b"image bytes")
    uris: tuple[pathlib.Path | str, ...] = (
        path,
        str(path),
        f"file://{path.as_posix()}",
    )
    for uri in uris:
        fs, resolved = pathlike_to_fs(uri, enforce_exists=True)
        assert resolved == path.as_posix()
        with fs.open(resolved, "rb") as stream:
            assert stream.read() == b"image bytes"


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
