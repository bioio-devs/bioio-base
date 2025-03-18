#!/usr/bin/env python
# -*- coding: utf-8 -*-

import typing
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Tuple
from xml.etree import ElementTree

from fsspec.core import url_to_fs

if TYPE_CHECKING:
    from fsspec.spec import AbstractFileSystem

from .types import PathLike

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
            raise FileNotFoundError(f"{fs.protocol}://{path}")

    # Get and store details
    # We do not return an AbstractBufferedFile (i.e. fs.open) as we do not want to have
    # any open file buffers _after_ any API call. API calls must themselves call
    # fs.open and complete their function during the context of the opened buffer.
    return fs, path


def search_for_node(
    parent: ElementTree.Element, tag: str, attributes: typing.Optional[dict] = None
) -> typing.Optional[ElementTree.Element]:
    """
    Recursive utility method for searching down an XML tree for a specific node
    that has the given tag and attributes.

    Parameters
    ----------
    parent: ElementTree.Element
        The parent node from which to begin the search.
    tag: str
        The XML tag to search for.
    attributes: dict, optional
        A dictionary of attributes to match. If provided, the node must match
        these attributes exactly.

    Returns
    -------
    ElementTree.Element or None
        The matching XML node if found, otherwise None.
    """
    if parent.tag == tag and (
        attributes is None or parent.attrib.items() >= attributes.items()
    ):
        return parent

    for child in parent:
        result = search_for_node(parent=child, tag=tag, attributes=attributes)
        if result is not None:
            return result

    return None
