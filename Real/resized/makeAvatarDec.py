from PIL import Image, ImageDraw
import numpy as np
import math
import random

# --- SETTINGS ---
canvas_size = 768
circle_diameter = 640
circle_radius = circle_diameter // 2
image_size = 128
frame_duration = 16
output_path = "ElliNet13_BouncingCircle_Chaotic.apng"
image_path = "ElliNet13-Resized.png"
steps_per_frame = 10
reflection_jitter_degrees = 15  # Increase jitter to break symmetry
required_bounces = 3
speed = 7.0  # Faster speed

# --- LOAD LOGO ---
original = Image.open(image_path).convert("RGBA")
logo = original.resize((image_size, image_size), Image.LANCZOS)

# Add red 1px border
bordered_logo = Image.new("RGBA", logo.size, (0, 0, 0, 0))
bordered_logo.paste(logo, (0, 0), mask=logo)
draw = ImageDraw.Draw(bordered_logo)
draw.rectangle([0, 0, image_size - 1, image_size - 1], outline="red")
logo = bordered_logo

# --- INITIAL SETUP ---
center = np.array([canvas_size / 2, canvas_size / 2])
pos = center - image_size / 2
angle = random.uniform(0, 2 * math.pi)
vel = speed * np.array([math.cos(angle), math.sin(angle)])

positions = []
bounce_count = 0
returning = False

while True:
    for _ in range(steps_per_frame):
        new_pos = pos + vel / steps_per_frame
        logo_center = new_pos + image_size / 2
        dist = np.linalg.norm(logo_center - center)

        if dist + image_size / 2 > circle_radius:
            # Bounce happened
            bounce_count += 1

            normal = (logo_center - center) / np.linalg.norm(logo_center - center)
            tangent = np.array([-normal[1], normal[0]])

            v_tangent = np.dot(vel, tangent) * tangent
            v_normal = np.dot(vel, normal) * normal

            # Reflect velocity
            vel = v_tangent - v_normal

            # Now add a random small rotation to velocity vector (break symmetry)
            angle_vel = math.atan2(vel[1], vel[0])
            jitter = math.radians(random.uniform(-reflection_jitter_degrees, reflection_jitter_degrees))
            angle_vel += jitter
            vel = speed * np.array([math.cos(angle_vel), math.sin(angle_vel)])

            # Move inside boundary slightly
            new_pos = pos + vel / steps_per_frame

        pos = new_pos

    positions.append(pos.copy())

    # Only return after required bounces and if velocity is pointing toward center
    if bounce_count >= required_bounces:
        logo_center = pos + image_size / 2
        to_center = center - logo_center
        to_center_unit = to_center / np.linalg.norm(to_center)
        vel_unit = vel / np.linalg.norm(vel)
        dot = np.dot(to_center_unit, vel_unit)
        if dot > 0.95:  # angle less than ~18°
            break

# Smooth return to center at same speed
start_pos = pos.copy()
logo_center = pos + image_size / 2
to_center = center - logo_center

distance = np.linalg.norm(to_center)
# Calculate steps needed based on speed & steps_per_frame
steps_needed = max(5, int(distance / (speed / steps_per_frame)))  # at least 5 frames for smoothness
# Optionally cap max steps to avoid too long slow return:
max_return_steps = 30
steps_needed = min(steps_needed, max_return_steps)

step_vel = to_center / steps_needed if steps_needed > 0 else np.array([0.0, 0.0])

for _ in range(steps_needed):
    pos += step_vel
    positions.append(pos.copy())

# --- RENDER FRAMES ---
frames = []
for pos in positions:
    frame = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    frame.paste(logo, tuple(pos.astype(int)), mask=logo)
    frames.append(frame)

# --- SAVE ---
frames[0].save(
    output_path,
    save_all=True,
    append_images=frames[1:],
    duration=frame_duration,
    loop=0,
    disposal=2,
    optimize=False,
)

print(f"Saved to {output_path} with {bounce_count} bounces and {len(frames)} frames.")
