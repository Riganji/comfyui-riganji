# Riganji — ComfyUI Custom Nodes

A small collection of utility nodes for ComfyUI.

---

## Nodes

### 🖼️ Image Resizer

Resizes images using **Lanczos resampling**. Image input is optional — the node can be used without it to generate an empty latent of a given size.

**Inputs**

| Name | Type | Description |
|---|---|---|
| `image` | IMAGE *(optional)* | Source image batch |
| `resize_method` | Dropdown | `Scale Factor` or `Set Size` |
| `scale_factor` | FLOAT | Multiplier for Scale Factor mode (e.g. `0.5` = half, `2.0` = double) |
| `set_width` | INT | Target width in pixels. `0` = auto (proportional to height) |
| `set_height` | INT | Target height in pixels. `0` = auto (proportional to width) |

**Outputs**

| Name | Type | Description |
|---|---|---|
| `IMAGE` | IMAGE | Resized image batch |
| `Width` | INT | Output width in pixels |
| `Height` | INT | Output height in pixels |
| `Latent Image` | LATENT | Empty latent sized for the output resolution (`w/8 × h/8`) |

The node displays the resulting resolution in real time as you adjust the parameters, without needing to run the pipeline.

---

### 📂 Load Images (Folder)

Loads an image sequence from a folder. Works like **VHS Load Images**, but additionally exposes the folder path as an output for passing downstream (e.g. to a save node).

**Inputs**

| Name | Type | Description |
|---|---|---|
| `directory` | STRING | Path to the folder (e.g. `X:\Frames\shot_01`) |
| `image_load_cap` | INT | Max number of images to load. `0` = all |
| `skip_first_images` | INT | Skip N images from the start |
| `select_every_nth` | INT | Load every Nth image. `1` = every image |

Supported formats: `.png` `.jpg` `.jpeg` `.webp` `.bmp` `.tiff`

Files are sorted in natural order (1, 2, 10 instead of 1, 10, 2). Uses `natsort` if installed, falls back to a built-in implementation.

**Outputs**

| Name | Type | Description |
|---|---|---|
| `IMAGE` | IMAGE | Stacked image batch |
| `directory` | STRING | The input folder path (pass-through) |
| `frame_count` | INT | Number of images actually loaded |

---

## Installation

**Option 1 — Clone**
```
cd ComfyUI/custom_nodes
git clone https://github.com/Riganji/comfyui-riganji.git Riganji
```

**Option 2 — Manual**

Download the repository as a ZIP and unpack it into `ComfyUI/custom_nodes/Riganji/`.

Restart ComfyUI after installing.
