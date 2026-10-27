#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Tuple
from urllib.parse import parse_qs, urlparse

from fsspec.core import url_to_fs

if TYPE_CHECKING:
    from fsspec.spec import AbstractFileSystem

from .types import ImageLike, PathLike

###############################################################################


def pathlike_to_fs(
    uri: PathLike,
    enforce_exists: bool = False,
    fs_kwargs: Dict[str, Any] = {},
) -> Tuple["AbstractFileSystem", str]:
    """
    Find and return the appropriate filesystem and path from a path-like object.

    Parameters
    ----------
    uri: PathLike
        The local or remote path or uri.
    enforce_exists: bool
        Check whether or not the resource exists, if not, raise FileNotFoundError.

    Returns
    -------
    fs: AbstractFileSystem
        The filesystem to operate on.
    path: str
        The full path to the target resource.
    fs_kwargs: Dict[str, Any]
        Any specific keyword arguments to pass down to the fsspec created filesystem.
        Default: {}

    Raises
    ------
    FileNotFoundError
        If enforce_exists is provided value True and the resource is not found or is
        unavailable.
    """
    # Convert paths to string to be handled by url_to_fs
    if isinstance(uri, Path):
        uri = str(uri)

    # Get details
    fs, path = url_to_fs(uri, **fs_kwargs)

    # Check file exists
    if enforce_exists:
        if not fs.exists(path):
            raise FileNotFoundError(f"{fs.protocol}://{path}")  # noqa: E231

    # Get and store details
    # We do not return an AbstractBufferedFile (i.e. fs.open) as we do not want to have
    # any open file buffers _after_ any API call. API calls must themselves call
    # fs.open and complete their function during the context of the opened buffer.
    return fs, path


def s3_https_to_s3(
    uri: ImageLike,
    fs_kwargs: Dict[str, Any] = {},
) -> Tuple[ImageLike, Dict[str, Any]]:
    """
    Rewrite an S3 HTTPS URL as an anonymous ``s3://`` URI.

    A directory can't be listed over HTTP(S), but the same objects can be over
    ``s3://``. Both ``https://s3.<region>.amazonaws.com/<bucket>/<key>`` and
    ``https://<bucket>.s3.<region>.amazonaws.com/<key>`` are recognized.

    Parameters
    ----------
    uri: ImageLike
        The image to rewrite. Anything other than an S3 HTTPS URL is returned
        unchanged.
    fs_kwargs: Dict[str, Any]
        Any specific keyword arguments to pass down to the fsspec created filesystem.
        Default: {}

    Returns
    -------
    uri: ImageLike
        The ``s3://`` URI, or the given uri if it is not an S3 HTTPS URL.
    fs_kwargs: Dict[str, Any]
        The given fs_kwargs, with ``anon=True`` added for a rewritten URL unless
        already set.

    Raises
    ------
    ValueError
        If the URL is presigned. A signature covers one object, so it can't be
        carried over to listing a directory.
    """
    if not isinstance(uri, str):
        return uri, fs_kwargs

    url = urlparse(uri)
    if url.scheme not in ("http", "https") or not url.netloc.endswith(".amazonaws.com"):
        return uri, fs_kwargs

    if url.netloc.startswith("s3."):
        bucket_and_key = url.path.lstrip("/")
    else:
        bucket, virtual_hosted, _ = url.netloc.rpartition(".s3.")
        if not virtual_hosted:
            return uri, fs_kwargs

        bucket_and_key = f"{bucket}{url.path}"

    if {"x-amz-signature", "signature"} & {k.lower() for k in parse_qs(url.query)}:
        raise ValueError(
            f"{uri} is a presigned URL, which only grants access to a single object. "
            "Use the s3:// URI or a public S3 URL to read a directory."
        )

    return "s3://" + bucket_and_key, {"anon": True, **fs_kwargs}
