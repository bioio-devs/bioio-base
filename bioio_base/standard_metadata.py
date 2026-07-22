import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional, Sequence

from ome_types import OME
from ome_types.model import UnitsTime

log = logging.getLogger(__name__)


@dataclass
class ChannelMetadata:
    """
    Per-channel acquisition metadata.

    Attributes
    ----------
    channel_id: Optional[str]
        The channel identifier (e.g. "Channel:0").
    name: Optional[str]
        The channel name (e.g. "EGFP").
    track: Optional[str]
        The acquisition track this channel belongs to (e.g. "Track:1"). Channels
        acquired together share a track; channels acquired individually have
        distinct tracks.
    dye_name: Optional[str]
        The dye / fluorophore name (e.g. "EGFP").
    channel_color: Optional[str]
        The display color as a hex ARGB string (e.g. "#FF00FF5B").
    contrast_method: Optional[str]
        The contrast method (e.g. "Fluorescence", "Brightfield").
    illumination_wavelength: Optional[str]
        The illumination wavelength range or peak in nm (e.g. "487-489").
    scan_direction: Optional[str]
        The scan direction for the acquisition (e.g. "Unidirectional"). This is an
        acquisition-wide value repeated for each channel.
    excitation_wavelength: Optional[str]
        The excitation wavelength in nm (e.g. "488").
    emission_wavelength: Optional[str]
        The emission wavelength in nm (e.g. "509").
    effective_na: Optional[str]
        The effective numerical aperture (e.g. "0.125").
    exposure_time: Optional[str]
        The raw exposure time as recorded by the format, unformatted. Units are
        format-specific (e.g. nanoseconds for CZI).
    imaging_device: Optional[str]
        The detector / camera used to acquire this channel (e.g. "Camera 1 (Back)").
    camera_adapter: Optional[str]
        The camera adapter of the imaging device (e.g. "1x Camera Adapter").
    section_thickness: Optional[str]
        The optical section thickness in micrometers.
    light_source_intensity: Optional[str]
        The light source intensity for this channel (e.g. "9.78 %"). When a channel
        uses multiple light sources the values are comma-joined.
    light_source: Optional[str]
        The light source(s) used for this channel (e.g. "LED1"). When a channel uses
        multiple light sources the names are comma-joined.

    FIELD_LABELS: dict[str, str]
        Mapping of the above attribute names to readable labels.
    """

    channel_id: Optional[str] = None
    name: Optional[str] = None
    track: Optional[str] = None
    dye_name: Optional[str] = None
    channel_color: Optional[str] = None
    contrast_method: Optional[str] = None
    illumination_wavelength: Optional[str] = None
    scan_direction: Optional[str] = None
    excitation_wavelength: Optional[str] = None
    emission_wavelength: Optional[str] = None
    effective_na: Optional[str] = None
    exposure_time: Optional[str] = None
    imaging_device: Optional[str] = None
    camera_adapter: Optional[str] = None
    section_thickness: Optional[str] = None
    light_source_intensity: Optional[str] = None
    light_source: Optional[str] = None

    FIELD_LABELS = {
        "channel_id": "Channel Id",
        "name": "Channel Name",
        "track": "Track",
        "dye_name": "Dye Name",
        "channel_color": "Channel Color",
        "contrast_method": "Contrast Method",
        "illumination_wavelength": "Illumination Wavelength",
        "scan_direction": "Scan Direction",
        "excitation_wavelength": "Excitation Wavelength",
        "emission_wavelength": "Emission Wavelength",
        "effective_na": "Effective NA",
        "exposure_time": "Exposure Time",
        "imaging_device": "Imaging Device",
        "camera_adapter": "Camera Adapter",
        "section_thickness": "Section Thickness",
        "light_source_intensity": "Light Source Intensity",
        "light_source": "Light Source",
    }

    def to_dict(self) -> dict:
        """Convert to a dictionary keyed by readable labels."""
        return {
            self.FIELD_LABELS[field]: getattr(self, field)
            for field in self.FIELD_LABELS
        }


@dataclass
class StandardMetadata:
    """
    A simple container for embedded metadata fields.

    Attributes
    ----------
    binning: Optional[str]
        Binning configuration.

    channels: Optional[Sequence[ChannelMetadata]]
        Per-channel metadata. Each entry describes a single channel; when
        serialized via to_dict, entries are expanded into nested dictionaries.

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

    imaging_datetime: Optional[datetime]
        Date and time this file was imaged.

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

    reflectors: Optional[Sequence[str]]
        Names of the reflectors installed on the microscope's turret.

    row: Optional[str]
        Row information.

    timelapse: Optional[bool]
        Is the data a timelapse?

    timelapse_interval: Optional[timedelta]
        Average time interval between timepoints.

    total_time_duration: Optional[timedelta]
        Total time duration of imaging, measured from the beginning of the first
        time point to the beginning of the final time point.

    FIELD_LABELS: dict[str, str]
        Mapping of the above attribute names to readable labels.
    """

    binning: Optional[str] = None
    channels: Optional[Sequence[ChannelMetadata]] = None
    column: Optional[str] = None
    dimensions_present: Optional[Sequence[str]] = None
    image_size_c: Optional[int] = None
    image_size_t: Optional[int] = None
    image_size_x: Optional[int] = None
    image_size_y: Optional[int] = None
    image_size_z: Optional[int] = None
    imaged_by: Optional[str] = None
    imaging_datetime: Optional[datetime] = None
    objective: Optional[str] = None
    pixel_size_x: Optional[float] = None
    pixel_size_y: Optional[float] = None
    pixel_size_z: Optional[float] = None
    position_index: Optional[int] = None
    reflectors: Optional[Sequence[str]] = None
    row: Optional[str] = None
    timelapse: Optional[bool] = None
    timelapse_interval: Optional[timedelta] = None
    total_time_duration: Optional[timedelta] = None

    FIELD_LABELS = {
        "binning": "Binning",
        "channels": "Channels",
        "column": "Column",
        "dimensions_present": "Dimensions Present",
        "image_size_c": "Image Size C",
        "image_size_t": "Image Size T",
        "image_size_x": "Image Size X",
        "image_size_y": "Image Size Y",
        "image_size_z": "Image Size Z",
        "imaged_by": "Imaged By",
        "imaging_datetime": "Imaging Datetime",
        "objective": "Objective",
        "pixel_size_x": "Pixel Size X",
        "pixel_size_y": "Pixel Size Y",
        "pixel_size_z": "Pixel Size Z",
        "position_index": "Position Index",
        "reflectors": "Reflectors",
        "row": "Row",
        "timelapse": "Timelapse",
        "timelapse_interval": "Timelapse Interval",
        "total_time_duration": "Total Time Duration",
    }

    @staticmethod
    def _serialize(value: Any) -> Any:
        """
        Recursively serialize a value, expanding nested objects that expose their
        own to_dict (and lists/tuples of them) into plain dictionaries.
        """
        to_dict = getattr(value, "to_dict", None)
        if callable(to_dict):
            return to_dict()
        if isinstance(value, (list, tuple)):
            return [StandardMetadata._serialize(item) for item in value]
        return value

    def to_dict(self) -> dict:
        """
        Convert the metadata into a dictionary using readable labels.

        Nested metadata objects (e.g. per-channel entries in ``channels``) that
        expose their own to_dict are expanded into nested dictionaries.

        Returns:
            dict: A mapping where keys are the readable labels defined in FIELD_LABELS,
                  and values are the corresponding metadata values.
        """
        return {
            self.FIELD_LABELS[field]: self._serialize(getattr(self, field))
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


def imaging_datetime(ome: OME) -> Optional[datetime]:
    """
    Extracts the acquisition datetime from the OME metadata.

    Returns
    -------
    Optional[datetime]
        The acquisition datetime as provided in the metadata,
        including its original timezone.

        None: if the acquisition datetime is not found or cannot be parsed.
    """
    try:
        img = ome.images[0]
        acq = img.acquisition_date
        return acq
    except Exception as exc:
        log.warning("Failed to extract Acquisition Datetime: %s", exc, exc_info=True)
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


def _convert_to_timedelta(delta_t: float, unit: Optional[UnitsTime]) -> timedelta:
    """
    Converts delta_t to a timedelta object based on the provided unit.
    """
    if unit is None:
        # Assume seconds if unit is None
        return timedelta(seconds=delta_t)

    unit_value = unit.value  # Access the string representation of the enum

    if unit_value == "ms":
        return timedelta(milliseconds=delta_t)
    elif unit_value == "µs":
        return timedelta(microseconds=delta_t)
    elif unit_value == "ns":
        return timedelta(microseconds=delta_t / 1000.0)
    else:
        # Default to seconds for unrecognized units
        log.warning("No units found for timedelta, defaulting to seconds.")
        return timedelta(seconds=delta_t)


def total_time_duration(ome: OME, scene_index: int) -> Optional[timedelta]:
    """
    Computes the total time duration from the beginning of the first
    timepoint to the beginning of the final timepoint.
    """
    try:
        image = ome.images[scene_index]
        planes = image.pixels.planes

        # Initialize variables to track the maximum the_t and corresponding plane
        max_t = -1
        target_plane = None

        for p in planes:
            if p.the_z == 0 and p.the_c == 0 and p.the_t is not None:
                if p.the_t > max_t:
                    max_t = p.the_t
                    target_plane = p

        if target_plane is None or target_plane.delta_t is None:
            return None

        return _convert_to_timedelta(target_plane.delta_t, target_plane.delta_t_unit)
    except Exception:
        return None


def timelapse_interval(ome: OME, scene_index: int) -> Optional[timedelta]:
    """
    Computes the average time interval between consecutive timepoints.
    """
    try:
        image = ome.images[scene_index]
        size_t = image.pixels.size_t
        if size_t is None or size_t < 2:
            return None

        total_duration = total_time_duration(ome, scene_index)
        if total_duration is None:
            return None

        return total_duration / (size_t - 1)
    except Exception:
        return None
