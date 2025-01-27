#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


class TimeInterval(NamedTuple):
    T: Optional[float]


class Scale(NamedTuple):
    T: Optional[float]
    C: Optional[float]
    Z: Optional[float]
    Y: Optional[float]
    X: Optional[float]
