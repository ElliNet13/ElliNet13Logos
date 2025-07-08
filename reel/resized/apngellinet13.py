import tempfile
import os
from PIL import Image, ImageSequence
import numpy as np

input_apng = "ElliNet13_BouncingCircle_Chaotic.apng"
output_apng = "ElliNet13_BouncingCircle_Chaotic_2color_transparent_fast.apng"

temp_folder = os.path.join(tempfile.gettempdir(), "ellinet13_apng_frames")

# Palette: 3 colors: transparent (index 0), black (1), #304FFF (2)
palette_colors = [
    (0, 0, 0),       # Transparent placeholder (index 0)
    (0, 0, 0),       # Black (index 1)
    (48, 79, 255),   # #304FFF (index 2)
]

def create_palette_image():
    palette = []
    for color in palette_colors:
        palette.extend(color)
    palette.extend([0, 0, 0] * (256 - len(palette_colors)))
    palette_img = Image.new("P", (1, 1))
    palette_img.putpalette(palette)
    return palette_img

def convert_frame_with_transparency_np(img, palette_img):
    img = img.convert("RGBA")
    arr = np.array(img)  # (H, W, 4)

    indexed_arr = np.zeros((arr.shape[0], arr.shape[1]), dtype=np.uint8)

    transparent_mask = (arr[:, :, 3] == 0)
    indexed_arr[transparent_mask] = 0  # transparency index

    black = np.array(palette_colors[1])
    blue = np.array(palette_colors[2])

    opaque_mask = ~transparent_mask
    rgb_pixels = arr[:, :, :3][opaque_mask]

    dist_black = np.sum((rgb_pixels - black) ** 2, axis=1)
    dist_blue = np.sum((rgb_pixels - blue) ** 2, axis=1)

    indexed_arr[opaque_mask] = np.where(dist_black < dist_blue, 1, 2)

    pal_img = Image.new("P", img.size)
    pal_img.putpalette(palette_img.getpalette())

    pal_pixels = pal_img.load()
    for y in range(img.height):
        for x in range(img.width):
            pal_pixels[x, y] = int(indexed_arr[y, x])  # Convert to Python int here!

    pal_img.info['transparency'] = 0
    return pal_img

def extract_frames(apng_path, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    frames = []
    with Image.open(apng_path) as im:
        for i, frame in enumerate(ImageSequence.Iterator(im)):
            frame_path = os.path.join(folder, f"frame_{i:03d}.png")
            frame.save(frame_path)
            frames.append(frame_path)
    return frames

def save_apng(frames, out_path, duration):
    imgs = [Image.open(f) for f in frames]
    imgs[0].save(out_path, save_all=True, append_images=imgs[1:], duration=duration, loop=0, disposal=2)

def main():
    print(f"Using temp folder: {temp_folder}")
    print("Extracting frames...")
    frames = extract_frames(input_apng, temp_folder)

    print("Creating palette image...")
    palette_img = create_palette_image()

    print("Converting frames with transparency and 2 colors (fast)...")
    new_frames = []
    for f in frames:
        img = Image.open(f)
        new_img = convert_frame_with_transparency_np(img, palette_img)
        new_path = f.replace(".png", "_2color_trans.png")
        new_img.save(new_path, optimize=True)
        new_frames.append(new_path)

    with Image.open(input_apng) as im:
        duration = im.info.get('duration', 100)

    print("Saving new APNG...")
    save_apng(new_frames, output_apng, duration)

    print(f"Done! Saved to {output_apng}")

if __name__ == "__main__":
    main()
