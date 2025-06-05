from pathlib import Path

import pytest
from ome_types import OME

from ..standard_metadata import binning, imaged_by, imaging_date, objective


@pytest.fixture
def sample_ome() -> OME:
    """
    Load the OME object from the JSON fixture.
    """
    json_path = Path(__file__).parent / "resources" / "sample.ome.json"
    raw = json_path.read_text(encoding="utf-8")
    return OME.model_validate_json(raw)


def test_binning(sample_ome: OME) -> None:
    result = binning(sample_ome)
    assert result == "1x1"


def test_imaged_by_with_explicit_ref(sample_ome: OME) -> None:
    result = imaged_by(sample_ome)
    assert result == "sara.carlson"


def test_imaging_date(sample_ome: OME) -> None:
    result = imaging_date(sample_ome)
    assert result == "2020-01-17"


def test_objective(sample_ome: OME) -> None:
    result = objective(sample_ome)
    assert result == "10x/0.45Air"
