import typing

import dask.array as da
import fsspec
import numpy as np
import xarray as xr

from .constants import METADATA_UNPROCESSED
from .dimensions import DEFAULT_DIMENSION_ORDER_LIST
from .reader import Reader


class NoopReader(Reader):
    """
    No-op (no operation) reader intended to be used in tests as a way to test utilities
    that utilize readers but are not trying to test any specific reader.

    NOT intended to be inherited by plug-in readers see ImageContainer instead.
    """

    _NUM_SCENES = 3
    _mock_data = np.arange(
        np.prod((_NUM_SCENES, 4, 5, 6, 7, 8)), dtype="uint16"
    ).reshape((_NUM_SCENES, 4, 5, 6, 7, 8))

    @staticmethod
    def _is_supported_image(
        fs: fsspec.AbstractFileSystem,
        path: str,
        **kwargs: typing.Any,
    ) -> bool:
        return True

    @property
    def scenes(self) -> typing.Tuple[str, ...]:
        return tuple(f"Image:{idx}" for idx in range(self._NUM_SCENES))

    def _read_delayed(self) -> xr.DataArray:
        return xr.DataArray(
            data=da.from_array(self._mock_data[self.current_scene_index]),
            dims=DEFAULT_DIMENSION_ORDER_LIST,
            attrs={METADATA_UNPROCESSED: {}},
        )

    def _read_immediate(self) -> xr.DataArray:
        return xr.DataArray(
            data=self._mock_data[self.current_scene_index],
            dims=DEFAULT_DIMENSION_ORDER_LIST,
            attrs={METADATA_UNPROCESSED: {}},
        )
