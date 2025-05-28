import logging
from dataclasses import dataclass
from typing import Optional, Sequence

from ome_types import OME

log = logging.getLogger(__name__)


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


def binning(ome: OME) -> Optional[str]:
    """
    Extracts the binning setting from the OME metadata.

    Returns
    -------
    Optional[str]
        The binning setting as a string. Returns None if not found.
    """
    try:
        # DetectorSettings under each Channel holds the binning info
        channels = ome.images[0].pixels.channels or []
        for channel in channels:
            ds = channel.detector_settings
            if ds and ds.binning:
                return str(ds.binning.value)
    except Exception as exc:
        log.warning("Failed to extract Binning setting: %s", exc, exc_info=True)
    return None


def imaged_by(ome: OME) -> Optional[str]:
    """
    Extracts the name of the experimenter (user who imaged the sample).

    Returns
    -------
    Optional[str]
        The username of the experimenter. Returns None if not found.
    """
    try:
        img = ome.images[0]
        # Prefer explicit ExperimenterRef if present
        if img.experimenter_ref and ome.experimenters:
            exp = next(
                (e for e in ome.experimenters if e.id == img.experimenter_ref.id), None
            )
            if exp and exp.user_name:
                return exp.user_name
        # Fallback to first Experimenter
        if ome.experimenters:
            return ome.experimenters[0].user_name
    except Exception as exc:
        log.warning("Failed to extract Imaged By: %s", exc, exc_info=True)
    return None


def imaging_date(ome: OME) -> Optional[str]:
    """
    Extracts the acquisition date from the OME metadata.

    Returns
    -------
    Optional[str]
        The acquisition date in ISO format (YYYY-MM-DD) adjusted to the local
        system timezone.

        None: if the acquisition date is not found or cannot be parsed.
    """
    try:
        img = ome.images[0]
        acq = img.acquisition_date
        local_time = acq.astimezone()
        return local_time.date().isoformat()
    except Exception as exc:
        log.warning("Failed to extract Acquisition Date: %s", exc, exc_info=True)
    return None


def objective(ome: OME) -> Optional[str]:
    """
    Extracts the microscope objective details.

    Returns
    -------
    Optional[str]
        The formatted objective magnification and numerical aperture.
        Returns the raw string (e.g. "40x/1.2W").
    """
    try:
        img = ome.images[0]
        instrs = ome.instruments or []
        instr = None
        # Prefer explicit InstrumentRef
        if img.instrument_ref:
            instr = next((i for i in instrs if i.id == img.instrument_ref.id), None)
        # Fallback to first Instrument
        if not instr and instrs:
            instr = instrs[0]
        if instr and instr.objectives:
            obj = instr.objectives[0]
            mag = round(float(obj.nominal_magnification))
            na = obj.lens_na
            imm = obj.immersion.value if obj.immersion else ""
            raw_obj = f"{mag}x/{na}{imm}"
            return raw_obj
    except Exception as exc:
        log.warning("Failed to extract Objective: %s", exc, exc_info=True)
    return None
