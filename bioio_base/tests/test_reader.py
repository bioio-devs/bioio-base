from typing import Any, Dict

import numpy as np
import pytest

from bioio_base import noop_reader, transforms


# NoopReader exposes mock data with dims TCZYX (shape 4, 5, 6, 7, 8).
@pytest.mark.parametrize(
    "order, kwargs",
    [
        ("ZYX", {"T": 0, "C": 1}),
        ("TCZYX", {"C": [0, 2], "Z": slice(0, 4, 2)}),
    ],
)
def test_get_image_data_matches_full_read_then_slice(
    order: str, kwargs: Dict[str, Any]
) -> None:
    reader = noop_reader.NoopReader("anything")
    expected = transforms.reshape_data(reader.data, reader.dims.order, order, **kwargs)
    actual = reader.get_image_data(order, **kwargs)
    np.testing.assert_array_equal(actual, expected)


def test_get_image_data_no_order_returns_full_data() -> None:
    reader = noop_reader.NoopReader("anything")
    np.testing.assert_array_equal(reader.get_image_data(), reader.data)


def test_read_indexed_default_matches_getitem() -> None:
    reader = noop_reader.NoopReader("anything")
    specs, _ = transforms.compute_dim_specs(
        reader.shape, reader.dims.order, "CZYX", T=1
    )
    np.testing.assert_array_equal(
        reader._read_indexed(reader.dims.order, specs),
        reader.data[tuple(specs)],
    )
