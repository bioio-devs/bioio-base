from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class StandardMetadata:
    """
    A simple container for embedded metadata fields using dataclass.

    Each metadata field is defined with an optional type.
    The FIELD_LABELS mapping is used to produce readable output via the to_dict method.
    """

    # Binning configuration.
    binning: Optional[str] = None

    # Column information.
    column: Optional[str] = None

    # List or sequence of dimension names.
    dimensions_present: Optional[Sequence[str]] = None

    # Channel dimension size.
    image_size_c: Optional[int] = None

    # Time dimension size.
    image_size_t: Optional[int] = None

    # Spatial X dimension size.
    image_size_x: Optional[int] = None

    # Spatial Y dimension size.
    image_size_y: Optional[int] = None

    # Spatial Z dimension size.
    image_size_z: Optional[int] = None

    # The experimentalist who produced this data.
    imaged_by: Optional[str] = None

    # Date this file was imaged.
    imaging_date: Optional[str] = None

    # Objective.
    objective: Optional[str] = None

    # Physical pixel size along X.
    pixel_size_x: Optional[float] = None

    # Physical pixel size along Y.
    pixel_size_y: Optional[float] = None

    # Physical pixel size along Z.
    pixel_size_z: Optional[float] = None

    # Position index, if applicable.
    position_index: Optional[int] = None

    # Row information.
    row: Optional[str] = None

    # Is the data a timelapse?
    timelapse: Optional[bool] = None

    # Time interval between frames.
    timelapse_interval: Optional[float] = None

    # Total time duration of imaging.
    total_time_duration: Optional[str] = None

    # Mapping of internal attribute names to readable labels.
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
