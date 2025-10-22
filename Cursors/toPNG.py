import os
from PIL import Image

# Create PNG output folder if it doesn't exist
output_folder = "PNG"
os.makedirs(output_folder, exist_ok=True)

# Loop through all files in the current directory
for filename in os.listdir("."):
    if filename.lower().endswith(".cur"):
        # Open the .cur file
        with Image.open(filename) as img:
            # Convert to PNG
            png_filename = os.path.join(output_folder, os.path.splitext(filename)[0] + ".png")
            img.save(png_filename, "PNG")
            print(f"Converted {filename} → {png_filename}")

print("All .cur files have been converted.")
