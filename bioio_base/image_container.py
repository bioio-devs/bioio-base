#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import dask.array as da
import numpy as np
import xarray as xr

from .dimensions import Dimensions
from .types import ImageLike, PhysicalPixelSizes

###############################################################################


class ImageContainer(ABC):
    def __init__(
        self,
        image: ImageLike,
        reader: Optional[Type["ImageContainer"]] = None,
        reconstruct_mosaic: bool = True,
        fs_kwargs: Dict[str, Any] = {},
        **kwargs: Any,
    ):
        pass

    @property
    @abstractmethod
    def scenes(self) -> Tuple[str, ...]:
        pass

    @property
    @abstractmethod
    def current_scene(self) -> str:
        pass

    @property
    @abstractmethod
    def current_scene_index(self) -> int:
        pass

    @abstractmethod
    def set_scene(self, scene_id: Union[str, int]) -> None:
        pass

    @property
    @abstractmethod
    def xarray_dask_data(self) -> xr.DataArray:
        pass

    @property
    @abstractmethod
    def xarray_data(self) -> xr.DataArray:
        pass

    @property
    @abstractmethod
    def dask_data(self) -> da.Array:
        pass

    @property
    @abstractmethod
    def data(self) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def dtype(self) -> np.dtype:
        pass

    @property
    @abstractmethod
    def shape(self) -> Tuple[int, ...]:
        pass

    @property
    @abstractmethod
    def dims(self) -> Dimensions:
        pass

    @abstractmethod
    def get_image_dask_data(
        self, dimension_order_out: Optional[str] = None, **kwargs: Any
    ) -> da.Array:
        pass

    @abstractmethod
    def get_image_data(
        self, dimension_order_out: Optional[str] = None, **kwargs: Any
    ) -> np.ndarray:
        pass

    @property
    @abstractmethod
    def metadata(self) -> Any:
        pass

    @property
    @abstractmethod
    def channel_names(self) -> Optional[List[str]]:
        pass

    @property
    @abstractmethod
    def physical_pixel_sizes(self) -> PhysicalPixelSizes:
        pass
