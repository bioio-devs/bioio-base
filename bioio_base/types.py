#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta
from pathlib import Path
from typing import List, NamedTuple, Optional, TypeAlias, Union

import dask.array as da
import numpy as np
import pint
import xarray as xr
from ome_types.units import ureg as ome_ureg

###############################################################################
# IO Types
###############################################################################

PathLike = Union[str, Path]
ArrayLike = Union[np.ndarray, da.Array]
MetaArrayLike = Union[ArrayLike, xr.DataArray]
ImageLike = Union[
    PathLike,
    ArrayLike,
    MetaArrayLike,
    List[MetaArrayLike],
    List[PathLike],
]

# Public type aliases for units
UnitRegistry: TypeAlias = pint.UnitRegistry
Unit: TypeAlias = pint.Unit

# Canonical global registry for BioIO, shared with OME-types
ureg: UnitRegistry = ome_ureg

###############################################################################
# Image Utility Types
###############################################################################


class PhysicalPixelSizes(NamedTuple):
    """
    Physical pixel sizes along the Z, Y, and X axes.
    """

    Z: Optional[float]
    Y: Optional[float]
    X: Optional[float]


TimeInterval = Optional[timedelta]


class Scale(NamedTuple):
    """
    Per-dimension scale factors for T, C, Z, Y, X.
    """

    T: Optional[float]
    C: Optional[float]
    Z: Optional[float]
    Y: Optional[float]
    X: Optional[float]


class DimensionProperty(NamedTuple):
    """
    Per-dimension metadata descriptor.

    Parameters
    ----------
    type:
        Semantic meaning of the dimension (e.g. "space", "time", "channel").
        This module does not enforce a fixed vocabulary.

    unit:
        A `pint.Unit` from the shared OME/BioIO unit registry (`ureg`),
        or None if the dimension unknown.
    """

    type: Optional[str]
    unit: Optional[Unit]


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
