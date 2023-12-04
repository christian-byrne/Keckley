from PIL import Image
import os

# Folder path containing images
folder_path = '/home/bymyself/p/morph-frame/data/projects/deniro-goodfellas-v1/frames/original/alpha-white_out'  # Replace with your folder path
output_filename = 'deniro-alpha_frames-grid.jpg'  # Output file name

# List all image files in the folder
image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]  # Add more extensions if needed

# Sort the image files
image_files.sort()  # You can change the sorting method if needed

# Calculate grid size (e.g., 3x3 grid)
grid_width = 22
grid_height = (len(image_files) + grid_width - 1) // grid_width

image_width = 45
image_height = 25

# Initialize the final grid image
grid_img = Image.new('RGB', (grid_width * image_width, grid_height * image_height))

# Populate the grid with images
for i, img_file in enumerate(image_files):
    img = Image.open(os.path.join(folder_path, img_file))
    # Resize image to fit the grid
    img.thumbnail((image_width, image_height))
    # Calculate position
    x = (i % grid_width) * image_width
    y = (i // grid_width) * image_height
    # Paste image onto the grid
    grid_img.paste(img, (x, y))

# Save the final grid image
grid_img.save(output_filename)
