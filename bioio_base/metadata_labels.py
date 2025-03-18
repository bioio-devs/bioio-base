from enum import Enum, unique


@unique
class MetadataLabels(Enum):
    DIMENSIONS_PRESENT = "Dimensions_Present"
    IMAGE_SIZE_C = "Image_Size_C"
    IMAGE_SIZE_T = "Image_Size_T"
    IMAGE_SIZE_X = "Image_Size_X"
    IMAGE_SIZE_Y = "Image_Size_Y"
    IMAGE_SIZE_Z = "Image_Size_Z"
    PIXEL_SIZE_X = "Pixel_Size_X"
    PIXEL_SIZE_Y = "Pixel_Size_Y"
    PIXEL_SIZE_Z = "Pixel_Size_Z"
    SCENE_INDEX = "Scene_Index"
    TIMELAPSE = "Timelapse"
    TIMELAPSE_INTERVAL = "Timelapse_Interval"
