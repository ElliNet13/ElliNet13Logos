from PIL import Image

input_path = "ElliNet13.jpeg"
output_path = "ElliNet13.ico"

img = Image.open(input_path)

sizes = [(16,16), (32,32), (48,48), (256,256)]

img.save(output_path, format="ICO", sizes=sizes)

print("Saved:", output_path)