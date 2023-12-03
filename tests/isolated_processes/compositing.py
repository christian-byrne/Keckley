from PIL import Image

# Load images
background = Image.open('bg-test.png')
alpha_channel = Image.open('alpha-test.png')

# Scale background to match alpha channel dimensions
background = background.resize(alpha_channel.size, Image.ANTIALIAS)

# Composite images using alpha channel
result = Image.alpha_composite(background.convert('RGBA'), alpha_channel)

# Save result
result.save('output.png')