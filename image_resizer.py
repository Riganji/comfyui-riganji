import torch
import numpy as np
from PIL import Image

class ImageResizer:
    """Image scaling using Lanczos resampling. Outputs image, width, height, and an empty latent."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "resize_method": (
                    ["Scale Factor", "Set Size"],
                    {"default": "Set Size"}
                ),
                "scale_factor": ("FLOAT", {
                    "default": 2.0,
                    "min": 0,
                    "max": 16.0,
                    "step": 0.1,
                    "display": "number",
                    "tooltip": "0.5 = Half Size and so on"
                }),
                "set_width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 16384,
                    "step": 1,
                    "display": "number",
                    "tooltip": "0 = auto (proportional to height)"
                }),
                "set_height": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 16384,
                    "step": 1,
                    "display": "number",
                    "tooltip": "0 = auto (proportional to width)"
                }),
            },
            "optional": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "LATENT")
    RETURN_NAMES = ("IMAGE", "Width", "Height", "Latent Image")
    FUNCTION = "upscale"
    CATEGORY = "image/upscaling"

    def upscale(self, resize_method: str, scale_factor: float,
                set_width: int, set_height: int, image: torch.Tensor = None):

        # source dimensions
        if image is not None:
            batch_size, height, width, channels = image.shape
            device = image.device
        else:
            if resize_method == "Scale Factor":
                raise ValueError(
                    "ImageResizer: connect an image or switch to Set Size mode"
                )
            if set_width == 0 or set_height == 0:
                raise ValueError(
                    "ImageResizer: set_width and set_height must be non-zero"
                )
            batch_size, height, width, channels = 1, set_height, set_width, 3
            device = torch.device("cpu")

        # target dimensions
        if resize_method == "Scale Factor":
            new_width  = int(round(width  * scale_factor))
            new_height = int(round(height * scale_factor))
        else:  # Set Size
            if set_width == 0 and set_height == 0:
                new_width, new_height = width, height
            elif set_width == 0:
                new_height = set_height
                new_width  = int(round(width * (set_height / height)))
            elif set_height == 0:
                new_width  = set_width
                new_height = int(round(height * (set_width / width)))
            else:
                new_width, new_height = set_width, set_height

        # Lanczos resize
        if image is not None:
            output_batch = []
            for i in range(batch_size):
                img_np      = (image[i].cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
                pil_img     = Image.fromarray(img_np)
                pil_resized = pil_img.resize((new_width, new_height), resample=Image.LANCZOS)
                resized_np  = np.array(pil_resized).astype(np.float32) / 255.0
                output_batch.append(torch.from_numpy(resized_np))
            out_tensor = torch.stack(output_batch, dim=0).to(device)
        else:
            out_tensor = torch.zeros((1, new_height, new_width, 3), device=device)

        # empty latent for the new resolution
        latent_h = new_height // 8
        latent_w = new_width  // 8
        latent   = {"samples": torch.zeros((batch_size, 4, latent_h, latent_w), device=device)}

        return (out_tensor, new_width, new_height, latent)


NODE_CLASS_MAPPINGS = {
    "ImageResizer": ImageResizer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageResizer": "Image Resizer"
}
