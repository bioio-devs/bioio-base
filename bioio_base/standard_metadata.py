from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class StandardMetadata:
    """
    A simple container for embedded metadata fields.

    Attributes
    ----------
    binning: Optional[str]
        Binning configuration.

    column: Optional[str]
        Column information.

    dimensions_present: Optional[Sequence[str]]
        List or sequence of dimension names.

    image_size_c: Optional[int]
        Channel dimension size.

    image_size_t: Optional[int]
        Time dimension size.

    image_size_x: Optional[int]
        Spatial X dimension size.

    image_size_y: Optional[int]
        Spatial Y dimension size.

    image_size_z: Optional[int]
        Spatial Z dimension size.

    imaged_by: Optional[str]
        The experimentalist who produced this data.

    imaging_date: Optional[str]
        Date this file was imaged.

    objective: Optional[str]
        Objective.

    pixel_size_x: Optional[float]
        Physical pixel size along X.

    pixel_size_y: Optional[float]
        Physical pixel size along Y.

    pixel_size_z: Optional[float]
        Physical pixel size along Z.

    position_index: Optional[int]
        Position index, if applicable.

    row: Optional[str]
        Row information.

    timelapse: Optional[bool]
        Is the data a timelapse?

    timelapse_interval: Optional[float]
        Time interval between frames, measured from the beginning of the first
        time point to the beginning of the second timepoint.

    total_time_duration: Optional[str]
        Total time duration of imaging, measured from the beginning of the first
        time point to the beginning of the final time point.

    FIELD_LABELS: dict[str, str]
        Mapping of the above attribute names to readable labels.
    """

    binning: Optional[str] = None
    column: Optional[str] = None
    dimensions_present: Optional[Sequence[str]] = None
    image_size_c: Optional[int] = None
    image_size_t: Optional[int] = None
    image_size_x: Optional[int] = None
    image_size_y: Optional[int] = None
    image_size_z: Optional[int] = None
    imaged_by: Optional[str] = None
    imaging_date: Optional[str] = None
    objective: Optional[str] = None
    pixel_size_x: Optional[float] = None
    pixel_size_y: Optional[float] = None
    pixel_size_z: Optional[float] = None
    position_index: Optional[int] = None
    row: Optional[str] = None
    timelapse: Optional[bool] = None
    timelapse_interval: Optional[float] = None
    total_time_duration: Optional[str] = None

    FIELD_LABELS = {
        "binning": "Binning",
        "column": "Column",
        "dimensions_present": "Dimensions Present",
        "image_size_c": "Image Size C",
        "image_size_t": "Image Size T",
        "image_size_x": "Image Size X",
        "image_size_y": "Image Size Y",
        "image_size_z": "Image Size Z",
        "imaged_by": "Imaged By",
        "imaging_date": "Imaging Date",
        "objective": "Objective",
        "pixel_size_x": "Pixel Size X",
        "pixel_size_y": "Pixel Size Y",
        "pixel_size_z": "Pixel Size Z",
        "position_index": "Position Index",
        "row": "Row",
        "timelapse": "Timelapse",
        "timelapse_interval": "Timelapse Interval",
        "total_time_duration": "Total Time Duration",
    }

    def to_dict(self) -> dict:
        """
        Convert the metadata into a dictionary using readable labels.

        Returns:
            dict: A mapping where keys are the readable labels defined in FIELD_LABELS,
                  and values are the corresponding metadata values.
        """
        return {
            self.FIELD_LABELS[field]: getattr(self, field)
            for field in self.FIELD_LABELS
        }
