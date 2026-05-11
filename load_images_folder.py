"""
LoadImagesFolder — Custom ComfyUI Node
=======================================
Loads images from a folder, identical to VHS Load Images (Folder),
but with an extra "directory" output port that passes the path string
to other nodes (e.g. FrameAutoSave).

Install: copy this file into ComfyUI/custom_nodes/riganji/load_images_folder.py
"""

import os
import hashlib
import numpy as np
from PIL import Image, ImageOps
import torch

try:
    from natsort import natsorted
    HAS_NATSORT = True
except ImportError:
    import re
    HAS_NATSORT = False


def _natural_sorted(files):
    """natsort if available, otherwise reliable fallback."""
    if HAS_NATSORT:
        return natsorted(files)
    # fallback: parse (prefix, main_num, sub_num, ext)
    import re
    def key(name):
        m = re.match(r'^(.*?)(\d+)(?:\.(\d+))?\.(\w+)$', name)
        if m:
            prefix, num, sub, ext = m.groups()
            return (prefix.lower(), int(num), int(sub) if sub else -1, ext.lower())
        return (name.lower(), 0, -1, '')
    return sorted(files, key=key)


class LoadImagesFolder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Path to folder with images (e.g. X:\\Frames\\00\\1)",
                }),
                "image_load_cap": ("INT", {
                    "default": 0, "min": 0, "max": 1_000_000,
                    "tooltip": "Max images to load (0 = all)",
                }),
                "skip_first_images": ("INT", {
                    "default": 0, "min": 0, "max": 1_000_000,
                    "tooltip": "Skip this many images from the start",
                }),
                "select_every_nth": ("INT", {
                    "default": 1, "min": 1, "max": 1_000_000,
                    "tooltip": "Take every Nth image (1 = every image)",
                }),
            }
        }

    RETURN_TYPES  = ("IMAGE", "STRING", "INT")
    RETURN_NAMES  = ("IMAGE", "directory", "frame_count")
    FUNCTION      = "load_images"
    CATEGORY      = "utils/video"

    @classmethod
    def IS_CHANGED(cls, directory, **kwargs):
        """
        Re-execute the node whenever directory contents change.
        Without this ComfyUI caches the output and skips re-reading on
        subsequent queue runs even if new files were added.
        """
        m = hashlib.md5()
        if os.path.isdir(directory):
            for fname in sorted(os.listdir(directory)):
                m.update(fname.encode())
        return m.hexdigest()

    def load_images(self, directory, image_load_cap, skip_first_images, select_every_nth):
        if not os.path.isdir(directory):
            raise ValueError(f"[LoadImagesFolder] Directory not found: {directory!r}")

        VALID_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}

        all_files = _natural_sorted(
            [f for f in os.listdir(directory)
             if os.path.splitext(f)[1].lower() in VALID_EXT]
        )

        if not all_files:
            raise ValueError(f"[LoadImagesFolder] No images found in: {directory!r}")

        print(f"[LoadImagesFolder] Sorted order ({len(all_files)} files): {all_files}")

        # ---------- apply skip / nth / cap ----------
        selected = all_files[skip_first_images::select_every_nth]
        if image_load_cap > 0:
            selected = selected[:image_load_cap]

        if not selected:
            raise ValueError("[LoadImagesFolder] No images left after skip/cap settings")

        # ---------- load & stack ----------
        frames = []
        for fname in selected:
            path = os.path.join(directory, fname)
            img  = Image.open(path)
            img  = ImageOps.exif_transpose(img)
            img  = img.convert("RGB")
            arr  = np.array(img, dtype=np.float32) / 255.0
            frames.append(arr)

        images_tensor = torch.from_numpy(np.stack(frames))
        frame_count   = images_tensor.shape[0]

        print(f"[LoadImagesFolder] Loaded {frame_count} image(s) from {directory!r}")

        return (images_tensor, directory, frame_count)


NODE_CLASS_MAPPINGS = {
    "LoadImagesFolder": LoadImagesFolder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadImagesFolder": "Load Images (Folder)",
}