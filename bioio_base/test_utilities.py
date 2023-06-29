#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, List, Optional, Tuple, Type, Union

import numpy as np
from distributed.protocol import deserialize, serialize
from fsspec.implementations.local import LocalFileSystem
from psutil import Process
from xarray.testing import assert_equal

from .reader import Reader
from .types import PathLike

###############################################################################


def check_local_file_not_open(reader: Reader) -> None:
    # Check that there are no open file pointers
    if isinstance(reader._fs, LocalFileSystem):
        proc = Process()
        assert str(reader._path) not in [f.path for f in proc.open_files()]


def check_can_serialize_reader(reader: Reader) -> None:
    # Dump and reconstruct
    reconstructed = deserialize(*serialize(reader))

    # Assert primary attrs are equal
    if reader._xarray_data is None:
        assert reconstructed._xarray_data is None
    else:
        assert_equal(reader._xarray_data, reconstructed._xarray_data)

    if reader._xarray_dask_data is None:
        assert reconstructed._xarray_dask_data is None
    else:
        assert_equal(reader._xarray_dask_data, reconstructed._xarray_dask_data)


def run_reader_checks(
    reader: Reader,
    set_scene: str,
    expected_scenes: Tuple[str, ...],
    expected_current_scene: str,
    expected_shape: Tuple[int, ...],
    expected_dtype: np.dtype,
    expected_dims_order: str,
    expected_channel_names: Optional[List[str]],
    expected_physical_pixel_sizes: Tuple[
        Optional[float], Optional[float], Optional[float]
    ],
    expected_metadata_type: Union[type, Tuple[Union[type, Tuple[Any, ...]], ...]],
) -> Reader:
    """
    A general suite of tests to run against readers.
    """

    # Check serdes
    check_can_serialize_reader(reader)

    # Set scene
    reader.set_scene(set_scene)

    # Check scene info
    assert reader.scenes == expected_scenes
    assert reader.current_scene == expected_current_scene

    # Check basics
    assert reader.shape == expected_shape
    assert reader.dtype == expected_dtype
    assert reader.dims.order == expected_dims_order
    assert reader.dims.shape == expected_shape
    assert reader.channel_names == expected_channel_names
    assert reader.physical_pixel_sizes == expected_physical_pixel_sizes
    assert isinstance(reader.metadata, expected_metadata_type)

    # Read different chunks
    zyx_chunk_from_delayed = reader.get_image_dask_data("ZYX").compute()
    cyx_chunk_from_delayed = reader.get_image_dask_data("CYX").compute()

    # Check image still not fully in memory
    assert reader._xarray_data is None

    # Read in mem then pull chunks
    zyx_chunk_from_mem = reader.get_image_data("ZYX")
    cyz_chunk_from_mem = reader.get_image_data("CYX")

    # Compare chunk reads
    np.testing.assert_array_equal(
        zyx_chunk_from_delayed,
        zyx_chunk_from_mem,
    )
    np.testing.assert_array_equal(
        cyx_chunk_from_delayed,
        cyz_chunk_from_mem,
    )

    # Check that the shape and dtype are expected after reading in full
    assert reader.data.shape == expected_shape
    assert reader.data.dtype == expected_dtype

    # Check serdes
    check_can_serialize_reader(reader)

    return reader


def run_reader_mosaic_checks(
    tiles_reader: Reader,
    stitched_reader: Reader,
    tiles_set_scene: str,
    stitched_set_scene: str,
) -> None:
    """
    A general suite of tests to run against readers that can stitch mosaic tiles.

    This tests uses in-memory numpy to compare. Test mosaics should be small enough to
    fit into memory.
    """
    # Set scenes
    tiles_reader.set_scene(tiles_set_scene)
    stitched_reader.set_scene(stitched_set_scene)

    # Get data subset
    from_tiles_stitched_data = tiles_reader.mosaic_data
    already_stitched_data = stitched_reader.data

    # Compare
    assert from_tiles_stitched_data.shape == already_stitched_data.shape
    np.testing.assert_array_equal(from_tiles_stitched_data, already_stitched_data)


def run_image_file_checks(
    Reader: Type[Reader],
    image: PathLike,
    set_scene: str,
    expected_scenes: Tuple[str, ...],
    expected_current_scene: str,
    expected_shape: Tuple[int, ...],
    expected_dtype: np.dtype,
    expected_dims_order: str,
    expected_channel_names: Optional[List[str]],
    expected_physical_pixel_sizes: Tuple[
        Optional[float], Optional[float], Optional[float]
    ],
    expected_metadata_type: Union[type, Tuple[Union[type, Tuple[Any, ...]], ...]],
) -> Reader:
    # Init container
    reader = Reader(image, fs_kwargs=dict(anon=True))

    # Check for file pointers
    check_local_file_not_open(reader)

    # Run array and metadata check operations
    run_reader_checks(
        reader=reader,
        set_scene=set_scene,
        expected_scenes=expected_scenes,
        expected_current_scene=expected_current_scene,
        expected_shape=expected_shape,
        expected_dtype=expected_dtype,
        expected_dims_order=expected_dims_order,
        expected_channel_names=expected_channel_names,
        expected_physical_pixel_sizes=expected_physical_pixel_sizes,
        expected_metadata_type=expected_metadata_type,
    )

    # Check for file pointers
    check_local_file_not_open(reader)

    return reader


def run_multi_scene_image_read_checks(
    Reader: Type[Reader],
    image: PathLike,
    first_scene_id: Union[str, int],
    first_scene_shape: Tuple[int, ...],
    first_scene_dtype: np.dtype,
    second_scene_id: Union[str, int],
    second_scene_shape: Tuple[int, ...],
    second_scene_dtype: np.dtype,
    allow_same_scene_data: bool = True,
) -> Reader:
    """
    A suite of tests to ensure that data is reset when switching scenes.
    """
    # Read file
    reader = Reader(image, fs_kwargs=dict(anon=True))

    check_local_file_not_open(reader)
    check_can_serialize_reader(reader)

    # Set scene
    reader.set_scene(first_scene_id)

    # Check basics
    if isinstance(first_scene_id, str):
        assert reader.current_scene == first_scene_id
    else:
        assert reader.current_scene_index == first_scene_id
    assert reader.shape == first_scene_shape
    assert reader.dtype == first_scene_dtype

    # Check that the shape and dtype are expected after reading in full
    first_scene_data = reader.data
    assert first_scene_data.shape == first_scene_shape
    assert first_scene_data.dtype == first_scene_dtype

    check_local_file_not_open(reader)
    check_can_serialize_reader(reader)

    # Change scene
    reader.set_scene(second_scene_id)

    # Check data was reset
    assert reader._xarray_dask_data is None
    assert reader._xarray_data is None
    assert reader._dims is None

    # Check basics
    if isinstance(second_scene_id, str):
        assert reader.current_scene == second_scene_id
    else:
        assert reader.current_scene_index == second_scene_id
    assert reader.shape == second_scene_shape
    assert reader.dtype == second_scene_dtype

    # Check that the shape and dtype are expected after reading in full
    second_scene_data = reader.data
    assert second_scene_data.shape == second_scene_shape
    assert second_scene_data.dtype == second_scene_dtype

    # Check that the first and second scene are not the same
    if not allow_same_scene_data:
        np.testing.assert_raises(
            AssertionError,
            np.testing.assert_array_equal,
            first_scene_data,
            second_scene_data,
        )

    check_local_file_not_open(reader)
    check_can_serialize_reader(reader)

    return reader


def run_no_scene_name_image_read_checks(
    Reader: Type[Reader],
    image: PathLike,
    first_scene_id: Union[str, int],
    first_scene_dtype: np.dtype,
    second_scene_id: Union[str, int],
    second_scene_dtype: np.dtype,
    allow_same_scene_data: bool = True,
) -> Reader:
    """
    A suite of tests to check that scene names are auto-filled when not present, and
    scene switching is reflected in current_scene_index.
    """
    # Read file
    reader = Reader(image, fs_kwargs=dict(anon=True))

    check_local_file_not_open(reader)
    check_can_serialize_reader(reader)

    # Set scene
    reader.set_scene(0)

    assert reader.current_scene_index == 0

    # Check basics
    if isinstance(first_scene_id, str):
        assert reader.current_scene == first_scene_id
    else:
        assert reader.current_scene_index == first_scene_id
    assert reader.dtype == first_scene_dtype

    # Check that the shape and dtype are expected after reading in full
    first_scene_data = reader.data
    assert first_scene_data.dtype == first_scene_dtype

    check_local_file_not_open(reader)
    check_can_serialize_reader(reader)

    # Change scene
    reader.set_scene(1)

    assert reader.current_scene_index == 1

    # Check data was reset
    assert reader._xarray_dask_data is None
    assert reader._xarray_data is None
    assert reader._dims is None

    # Check basics
    if isinstance(second_scene_id, str):
        assert reader.current_scene == second_scene_id
    else:
        assert reader.current_scene_index == second_scene_id
    assert reader.dtype == second_scene_dtype

    # Check that the shape and dtype are expected after reading in full
    second_scene_data = reader.data
    assert second_scene_data.dtype == second_scene_dtype

    # Check that the first and second scene are not the same
    if not allow_same_scene_data:
        np.testing.assert_raises(
            AssertionError,
            np.testing.assert_array_equal,
            first_scene_data,
            second_scene_data,
        )

    check_local_file_not_open(reader)
    check_can_serialize_reader(reader)

    return reader