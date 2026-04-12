from PIL import Image
import math
import os

# --- SETTINGS ---
canvas_size = round(768 / 1.55)  # 384
circle_diameter = round(640 / 1.55)  # 320
circle_radius = circle_diameter // 2  # 160
image_path = "ElliNet13-Resized.png"
output_path = os.path.expanduser('~') + "/Downloads/ElliNet13_Spin_Interpolated.apng"

fps = 30
duration_secs = 6
num_frames = fps * duration_secs
frame_duration = int(1000 / fps)  # milliseconds per frame

scale_factor = 0.25  # scale image to 25% size

# Load and scale image
img_original = Image.open(image_path).convert("RGBA")
img = img_original.resize(
    (int(img_original.width * scale_factor), int(img_original.height * scale_factor)),
    Image.LANCZOS
)
img_w, img_h = img.size

# Center of canvas
center_x = canvas_size // 2
center_y = canvas_size // 2

# Create animation frames
frames = []

for i in range(num_frames):
    # Angle for this frame (start at top)
    angle = 2 * math.pi * (i / num_frames) - math.pi / 2

    x = center_x + circle_radius * math.cos(angle) - img_w / 2
    y = center_y + circle_radius * math.sin(angle) - img_h / 2

    # Clamp coordinates so image is fully inside canvas
    x = max(0, min(int(x), canvas_size - img_w))
    y = max(0, min(int(y), canvas_size - img_h))

    # Create transparent frame
    frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    frame.paste(img, (x, y), img)
    frames.append(frame)

# Save as APNG with explicit APNG format, no optimization
frames[0].save(
    output_path,
    save_all=True,
    append_images=frames[1:],
    duration=frame_duration,
    loop=0,
    disposal=2,
    optimize=False,
    format="PNG"
)

print(f"✅ Saved smooth 30fps APNG to: {output_path}")
