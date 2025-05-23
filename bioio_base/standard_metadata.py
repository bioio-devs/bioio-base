import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Sequence
from zoneinfo import ZoneInfo

from lxml.etree import XML, _Element
from ome_types import OME

# XML namespace for OME
OME_NS = {"": "http://www.openmicroscopy.org/Schemas/OME/2016-06"}

log = logging.getLogger(__name__)

# Valid objectives for comparison when parsing Objective
VALID_OBJECTIVES = [
    "63x/1.2W",
    "20x/0.8",
    "40x/1.2W",
    "100x/1.25W",
    "100x/1.46Oil",
    "44.83x/1.0W",
    "5x/0.12",
    "10x/0.45",
]


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


# Helper functions for OME metadata extraction


def get_metadata_element(ome_metadata: OME, path: str) -> Optional[_Element]:
    """
    Gets the first occurrence of the given XML path if one exists.
    """
    xml = XML(ome_metadata.to_xml())
    return xml.find(path, OME_NS)


def binning(ome_metadata: OME) -> Optional[str]:
    """
    Extracts the binning setting from the OME metadata.
    Returns
    -------
    Optional[str]
        The binning setting as a string. Returns None if not found.
    """
    try:
        el = get_metadata_element(
            ome_metadata, "./Image/Pixels/Channel/DetectorSettings"
        )
        if el is not None:
            return el.get("Binning", None)
    except Exception as exc:
        log.warning("Failed to extract Binning setting: %s", exc, exc_info=True)
    return None


def imaged_by(ome_metadata: OME) -> Optional[str]:
    """
    Extracts the name of the experimenter (user who imaged the sample).
    Returns
    -------
    Optional[str]
        The username of the experimenter. Returns None if not found.
    """
    try:
        el = get_metadata_element(ome_metadata, "./Experimenter")
        if el is not None:
            return el.get("UserName", None)
    except Exception as exc:
        log.warning("Failed to extract Imaged By: %s", exc, exc_info=True)
    return None


def imaging_date(ome_metadata: OME) -> Optional[str]:
    """
    Extracts the acquisition date from the OME metadata.
    Returns
    -------
    Optional[str]
        The acquisition date in ISO format (YYYY-MM-DD) adjusted to Pacific Time.
        Returns None if the acquisition date is not found or cannot be parsed.
    """
    try:
        el = get_metadata_element(ome_metadata, "./Image/AcquisitionDate")
        if el is not None and el.text:
            utc_time = datetime.fromisoformat(el.text.replace("Z", "+00:00"))
            pacific_time = utc_time.astimezone(ZoneInfo("America/Los_Angeles"))
            return pacific_time.date().isoformat()
    except ValueError as exc:
        log.warning("Failed to parse Acquisition Date: %s", exc, exc_info=True)
    except Exception as exc:
        log.warning("Failed to extract Acquisition Date: %s", exc, exc_info=True)
    return None


def objective(ome_metadata: OME) -> Optional[str]:
    """
    Extracts the microscope objective details.
    Returns
    -------
    Optional[str]
        The formatted objective magnification and numerical aperture.
        Returns None if not found.
    """
    try:
        el = get_metadata_element(ome_metadata, "./Instrument/Objective")
        if el is not None:
            nominal = el.get("NominalMagnification")
            lens_na = el.get("LensNA")
            immersion = el.get("Immersion")
            immersion_suffix = ""
            if immersion == "Oil":
                immersion_suffix = "Oil"
            elif immersion == "Water":
                immersion_suffix = "W"
            if nominal is not None and lens_na is not None:
                raw_obj = f"{round(float(nominal))}x/{float(lens_na)}{immersion_suffix}"
                if raw_obj in VALID_OBJECTIVES:
                    return raw_obj
                for valid in VALID_OBJECTIVES:
                    if raw_obj in valid:
                        return valid
    except Exception as exc:
        log.warning("Failed to extract Objective: %s", exc, exc_info=True)
    return None
