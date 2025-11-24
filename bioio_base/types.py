#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta
from pathlib import Path
from typing import List, NamedTuple, Optional, Union

import dask.array as da
import numpy as np
import xarray as xr

###############################################################################

# IO Types
PathLike = Union[str, Path]
ArrayLike = Union[np.ndarray, da.Array]
MetaArrayLike = Union[ArrayLike, xr.DataArray]
ImageLike = Union[
    PathLike, ArrayLike, MetaArrayLike, List[MetaArrayLike], List[PathLike]
]


# Image Utility Types
class PhysicalPixelSizes(NamedTuple):
    Z: Optional[float]
    Y: Optional[float]
    X: Optional[float]


TimeInterval = Optional[timedelta]


class Scale(NamedTuple):
    T: Optional[float]
    C: Optional[float]
    Z: Optional[float]
    Y: Optional[float]
    X: Optional[float]


class DimensionProperty(NamedTuple):
    """
    Per-dimension descriptor for dimension metadata.

    value:
        The numeric value for this dimension (e.g. from Scale or PhysicalPixelSizes).
    type:
        Semantic meaning of the dimension (e.g. "spatial", "temporal", "channel").
    unit:
        Unit string associated with the value (e.g. "micrometer", "second", "index").
    """

    value: Optional[float]
    type: Optional[str]
    unit: Optional[str]


class DimensionProperties(NamedTuple):
    """
    Container for dimension properties for all supported dims.

    These align with the standard bioio dimension order (T, C, Z, Y, X).
    """

    T: DimensionProperty
    C: DimensionProperty
    Z: DimensionProperty
    Y: DimensionProperty
    X: DimensionProperty
