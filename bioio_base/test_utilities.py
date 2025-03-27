#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, List, Optional, Tuple, Type, Union

import numpy as np
from distributed.protocol import deserialize, serialize
from fsspec.implementations.local import LocalFileSystem
from psutil import Process
from xarray.testing import assert_equal

from .image_container import ImageContainer
from .reader import Reader
from .types import PathLike

###############################################################################


def check_local_file_not_open(image_container: ImageContainer) -> None:
    if not hasattr(image_container, "_fs") or not hasattr(image_container, "_path"):
        if not hasattr(image_container, "reader"):
            raise ValueError(
                "Expected 'image_container' to have '_fs' and "
                "'_path' attributes or a 'reader' attribute"
            )

        image_container = image_container.reader
        if not hasattr(image_container, "_fs") or not hasattr(image_container, "_path"):
            raise ValueError(
                "Expected 'image_container' to have '_fs' and "
                "'_path' attributes or a 'reader' attribute with "
                "'_fs' and '_path' attributes"
            )

    # Check that there are no open file pointers
    if isinstance(image_container._fs, LocalFileSystem):
        proc = Process()
        assert str(image_container._path) not in [f.path for f in proc.open_files()]


def check_can_serialize_image_container(image_container: ImageContainer) -> None:
    # Dump and reconstruct
    reconstructed = deserialize(*serialize(image_container))

    # Assert primary attrs are equal
    if image_container.xarray_data is None:
        assert reconstructed.xarray_data is None
    else:
        assert_equal(image_container.xarray_data, reconstructed.xarray_data)

    if image_container.xarray_dask_data is None:
        assert reconstructed.xarray_dask_data is None
    else:
        assert_equal(image_container.xarray_dask_data, reconstructed.xarray_dask_data)


def run_image_container_checks(
    image_container: ImageContainer,
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
    set_resolution_level: int = 0,
    expected_current_resolution_level: int = 0,
    expected_resolution_levels: Tuple[int, ...] = (0,),
) -> ImageContainer:
    """
    A general suite of tests to run against readers.
    """

    # Check serdes
    check_can_serialize_image_container(image_container)

    # Set scene
    image_container.set_scene(set_scene)

    # Check scene info
    assert image_container.scenes == expected_scenes
    assert image_container.current_scene == expected_current_scene

    # Set resolution level
    image_container.set_resolution_level(set_resolution_level)

    # Check resolution level info
    assert image_container.resolution_levels == expected_resolution_levels
    assert image_container.current_resolution_level == expected_current_resolution_level

    # Check basics
    assert image_container.shape == expected_shape
    assert image_container.dtype == expected_dtype
    assert image_container.dims.order == expected_dims_order
    assert image_container.dims.shape == expected_shape
    assert image_container.channel_names == expected_channel_names
    assert image_container.physical_pixel_sizes == expected_physical_pixel_sizes
    assert isinstance(image_container.metadata, expected_metadata_type)

    # Read different chunks
    zyx_chunk_from_delayed = image_container.get_image_dask_data("ZYX").compute()
    cyx_chunk_from_delayed = image_container.get_image_dask_data("CYX").compute()

    # Read in mem then pull chunks
    zyx_chunk_from_mem = image_container.get_image_data("ZYX")
    cyz_chunk_from_mem = image_container.get_image_data("CYX")

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
    assert image_container.data.shape == expected_shape
    assert image_container.data.dtype == expected_dtype

    # Check serdes
    check_can_serialize_image_container(image_container)

    return image_container


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
    ImageContainer: Type[ImageContainer],
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
    set_resolution_level: int = 0,
    expected_current_resolution_level: int = 0,
    expected_resolution_levels: Tuple[int, ...] = (0,),
    reader_kwargs: dict = dict(fs_kwargs=dict(anon=True)),
) -> ImageContainer:
    # Init container
    image_container = ImageContainer(image, **reader_kwargs)

    # Check for file pointers
    check_local_file_not_open(image_container)

    # Run array and metadata check operations
    run_image_container_checks(
        image_container=image_container,
        set_scene=set_scene,
        set_resolution_level=set_resolution_level,
        expected_scenes=expected_scenes,
        expected_current_scene=expected_current_scene,
        expected_resolution_levels=expected_resolution_levels,
        expected_current_resolution_level=expected_current_resolution_level,
        expected_shape=expected_shape,
        expected_dtype=expected_dtype,
        expected_dims_order=expected_dims_order,
        expected_channel_names=expected_channel_names,
        expected_physical_pixel_sizes=expected_physical_pixel_sizes,
        expected_metadata_type=expected_metadata_type,
    )

    # Check for file pointers
    check_local_file_not_open(image_container)

    return image_container


def run_multi_scene_image_read_checks(
    ImageContainer: Type[ImageContainer],
    image: PathLike,
    first_scene_id: Union[str, int],
    first_scene_shape: Tuple[int, ...],
    first_scene_dtype: np.dtype,
    second_scene_id: Union[str, int],
    second_scene_shape: Tuple[int, ...],
    second_scene_dtype: np.dtype,
    allow_same_scene_data: bool = True,
    reader_kwargs: dict = dict(fs_kwargs=dict(anon=True)),
) -> ImageContainer:
    """
    A suite of tests to ensure that data is reset when switching scenes.
    """
    # Read file
    image_container = ImageContainer(image, **reader_kwargs)

    check_local_file_not_open(image_container)
    check_can_serialize_image_container(image_container)

    # Set scene
    image_container.set_scene(first_scene_id)

    # Check basics
    if isinstance(first_scene_id, str):
        assert image_container.current_scene == first_scene_id
    else:
        assert image_container.current_scene_index == first_scene_id
    assert image_container.shape == first_scene_shape
    assert image_container.dtype == first_scene_dtype

    # Check that the shape and dtype are expected after reading in full
    first_scene_data = image_container.data
    assert first_scene_data.shape == first_scene_shape
    assert first_scene_data.dtype == first_scene_dtype

    check_local_file_not_open(image_container)
    check_can_serialize_image_container(image_container)

    # Change scene
    image_container.set_scene(second_scene_id)

    # Check basics
    if isinstance(second_scene_id, str):
        assert image_container.current_scene == second_scene_id
    else:
        assert image_container.current_scene_index == second_scene_id
    assert image_container.shape == second_scene_shape
    assert image_container.dtype == second_scene_dtype

    # Check that the shape and dtype are expected after reading in full
    second_scene_data = image_container.data
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

    check_local_file_not_open(image_container)
    check_can_serialize_image_container(image_container)

    return image_container


def run_no_scene_name_image_read_checks(
    ImageContainer: Type[ImageContainer],
    image: PathLike,
    first_scene_id: Union[str, int],
    first_scene_dtype: np.dtype,
    second_scene_id: Union[str, int],
    second_scene_dtype: np.dtype,
    allow_same_scene_data: bool = True,
    reader_kwargs: dict = dict(fs_kwargs=dict(anon=True)),
) -> ImageContainer:
    """
    A suite of tests to check that scene names are auto-filled when not present, and
    scene switching is reflected in current_scene_index.
    """
    # Read file
    image_container = ImageContainer(image, **reader_kwargs)

    check_local_file_not_open(image_container)
    check_can_serialize_image_container(image_container)

    # Set scene
    image_container.set_scene(0)

    assert image_container.current_scene_index == 0

    # Check basics
    if isinstance(first_scene_id, str):
        assert image_container.current_scene == first_scene_id
    else:
        assert image_container.current_scene_index == first_scene_id
    assert image_container.dtype == first_scene_dtype

    # Check that the shape and dtype are expected after reading in full
    first_scene_data = image_container.data
    assert first_scene_data.dtype == first_scene_dtype

    check_local_file_not_open(image_container)
    check_can_serialize_image_container(image_container)

    # Change scene
    image_container.set_scene(1)

    assert image_container.current_scene_index == 1

    # Check basics
    if isinstance(second_scene_id, str):
        assert image_container.current_scene == second_scene_id
    else:
        assert image_container.current_scene_index == second_scene_id
    assert image_container.dtype == second_scene_dtype

    # Check that the shape and dtype are expected after reading in full
    second_scene_data = image_container.data
    assert second_scene_data.dtype == second_scene_dtype

    # Check that the first and second scene are not the same
    if not allow_same_scene_data:
        np.testing.assert_raises(
            AssertionError,
            np.testing.assert_array_equal,
            first_scene_data,
            second_scene_data,
        )

    check_local_file_not_open(image_container)
    check_can_serialize_image_container(image_container)

    return image_container
