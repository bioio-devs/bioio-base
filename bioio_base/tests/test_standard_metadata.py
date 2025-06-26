from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import pytest
from ome_types import OME

from ..standard_metadata import (
    binning,
    imaged_by,
    imaging_datetime,
    objective,
    timelapse_interval,
    total_time_duration,
)


@pytest.mark.parametrize(
    (
        "file_name",
        "expected_binning",
        "expected_imaged_by",
        "expected_imaging_datetime",
        "expected_objective",
        "expected_time_interval",
        "expected_total_time_duration",
    ),
    [
        (
            "sample.ome.json",
            "1x1",
            "sara.carlson",
            datetime(2020, 1, 18, 0, 16, 29, 771361, tzinfo=timezone.utc),
            "10x/0.45Air",
            None,
            None,
        ),
        (
            "sample_timelapse.ome.json",
            None,
            None,
            None,
            None,
            timedelta(seconds=1.12),
            timedelta(seconds=54.91),
        ),
        (
            "sample_timelapse_20_sec_interval.json",
            "2x2",
            "sara.carlson",
            datetime(2020, 7, 1, 21, 58, 52, 631000),
            "100x/1.25Water",
            timedelta(seconds=20.07),
            timedelta(seconds=180.70),
        ),
    ],
)
def test_ome_metadata(
    file_name: str,
    expected_binning: Optional[str],
    expected_imaged_by: Optional[str],
    expected_imaging_datetime: Optional[datetime],
    expected_objective: Optional[str],
    expected_time_interval: Optional[timedelta],
    expected_total_time_duration: Optional[timedelta],
) -> None:
    """
    Parameterized test for OME metadata extraction functions.
    """
    # Load the OME object from the JSON file
    json_path = Path(__file__).parent / "resources" / file_name
    raw = json_path.read_text(encoding="utf-8")
    ome = OME.model_validate_json(raw)

    # Test binning
    assert binning(ome) == expected_binning

    # Test imaged_by
    assert imaged_by(ome) == expected_imaged_by

    # Test imaging_datetime
    assert imaging_datetime(ome) == expected_imaging_datetime

    # Test objective
    assert objective(ome) == expected_objective

    # Test timelapse_interval
    interval = timelapse_interval(ome, 0)
    if expected_time_interval is None:
        assert interval is None
    else:
        assert interval is not None
        assert interval.total_seconds() == pytest.approx(
            expected_time_interval.total_seconds(), abs=1e-2
        )

    # Test total_time_duration
    duration = total_time_duration(ome, 0)
    if expected_total_time_duration is None:
        assert duration is None
    else:
        assert duration is not None
        assert duration.total_seconds() == pytest.approx(
            expected_total_time_duration.total_seconds(), abs=1e-2
        )
