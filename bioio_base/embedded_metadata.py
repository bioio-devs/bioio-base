from typing import (
    Any,
    ClassVar,
    Generic,
    Optional,
    Sequence,
    Set,
    TypeVar,
    Union,
    overload,
)

from .dimensions import DimensionNames

# -----------------------------------------------------------------------------
# Descriptor for metadata fields.
# -----------------------------------------------------------------------------
T = TypeVar("T")  # Generic type variable to enable type-safe storage of metadata


class MetadataField(Generic[T]):
    def __init__(self, label: str, default: Optional[T] = None) -> None:
        self.label = label
        self.default = default
        self.private_name: Optional[str] = None

    def __set_name__(self, owner: Any, name: str) -> None:
        self.private_name = "_" + name

    @overload
    def __get__(self, instance: None, owner: Any) -> "MetadataField[T]":
        ...

    @overload
    def __get__(self, instance: Any, owner: Any) -> Optional[T]:
        ...

    def __get__(
        self, instance: Any, owner: Any = None
    ) -> Union["MetadataField[T]", Optional[T]]:
        if instance is None:
            return self  # When accessed on the class, return the descriptor.
        return instance.__dict__.get(self.private_name, self.default)

    def __set__(self, instance: Any, value: T) -> None:
        instance.__dict__[self.private_name] = value


# -----------------------------------------------------------------------------
# EmbeddedMetadata class with definitive (closed) fields.
# -----------------------------------------------------------------------------
class EmbeddedMetadata:
    # Calculated metadata fields.
    dimensions_present: MetadataField[Optional[Sequence[str]]] = MetadataField(
        "Dimensions Present"
    )
    image_size_c: MetadataField[Optional[int]] = MetadataField("Image Size C")
    image_size_t: MetadataField[Optional[int]] = MetadataField("Image Size T")
    image_size_x: MetadataField[Optional[int]] = MetadataField("Image Size X")
    image_size_y: MetadataField[Optional[int]] = MetadataField("Image Size Y")
    image_size_z: MetadataField[Optional[int]] = MetadataField("Image Size Z")
    pixel_size_x: MetadataField[Optional[float]] = MetadataField("Pixel Size X")
    pixel_size_y: MetadataField[Optional[float]] = MetadataField("Pixel Size Y")
    pixel_size_z: MetadataField[Optional[float]] = MetadataField("Pixel Size Z")
    timelapse: MetadataField[Optional[bool]] = MetadataField("Timelapse")

    # Predefined metadata fields for user override.
    objective: MetadataField[Optional[str]] = MetadataField("Objective")
    binning: MetadataField[Optional[str]] = MetadataField("Binning")
    column: MetadataField[Optional[str]] = MetadataField("Column")
    imaged_by: MetadataField[Optional[str]] = MetadataField("Imaged By")
    imaging_date: MetadataField[Optional[str]] = MetadataField("Imaging Date")
    position_index: MetadataField[Optional[int]] = MetadataField("Position Index")
    row: MetadataField[Optional[str]] = MetadataField("Row")
    total_time_duration: MetadataField[Optional[str]] = MetadataField(
        "Total Time Duration"
    )
    well: MetadataField[Optional[str]] = MetadataField("Well")
    mosaic_tile: MetadataField[Optional[int]] = MetadataField("Mosaic Tile")

    _allowed_fields: ClassVar[Set[str]]  # declare _allowed_fields as a class variable

    def __setattr__(self, name: str, value: Any) -> None:
        # Enforce that only allowed fields (precomputed in _allowed_fields) can be set.
        if name not in self.__class__._allowed_fields:
            raise AttributeError(
                f"Cannot set attribute '{name}'. Only predefined fields are allowed."
            )
        super().__setattr__(name, value)

    @classmethod
    def from_reader(cls, reader: Any) -> "EmbeddedMetadata":
        """
        Create an EmbeddedMetadata instance using values from the reader.
        """
        meta = cls()
        dims = reader.dims
        meta.dimensions_present = reader.dims.order
        meta.image_size_c = getattr(dims, DimensionNames.Channel, None)
        meta.image_size_t = getattr(dims, DimensionNames.Time, None)
        meta.image_size_x = getattr(dims, DimensionNames.SpatialX, None)
        meta.image_size_y = getattr(dims, DimensionNames.SpatialY, None)
        meta.image_size_z = getattr(dims, DimensionNames.SpatialZ, None)
        meta.mosaic_tile = getattr(dims, DimensionNames.MosaicTile, None)
        meta.timelapse = meta.image_size_t is not None and meta.image_size_t > 0
        # Assume reader.physical_pixel_sizes has attributes X, Y, and Z.
        meta.pixel_size_x = reader.physical_pixel_sizes.X
        meta.pixel_size_y = reader.physical_pixel_sizes.Y
        meta.pixel_size_z = reader.physical_pixel_sizes.Z
        return meta

    def __repr__(self) -> str:
        field_values = []
        for attr, descriptor in self.__class__.__dict__.items():
            if isinstance(descriptor, MetadataField):
                label = descriptor.label
                value = getattr(self, attr)
                field_values.append(f"{label}={value!r}")
        return f"EmbeddedMetadata({', '.join(field_values)})"


# -----------------------------------------------------------------------------
# Helper: compute allowed fields from the class dictionary.
# -----------------------------------------------------------------------------
def _compute_allowed_fields(cls: type) -> set[str]:
    allowed = set()
    for name, value in cls.__dict__.items():
        if isinstance(value, MetadataField):
            allowed.add(name)
            if value.private_name is not None:
                allowed.add(value.private_name)
    return allowed


# Manually compute and assign _allowed_fields for the base class.
EmbeddedMetadata._allowed_fields = _compute_allowed_fields(EmbeddedMetadata)
