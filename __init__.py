from .load_images_folder import LoadImagesFolder
from .image_resizer import ImageResizer

NODE_CLASS_MAPPINGS = {
    "LoadImagesFolder": LoadImagesFolder,
    "ImageResizer": ImageResizer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImagesFolder": "Load Images (Riganji)",
    "ImageResizer": "Image Resizer (Riganji)",
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]