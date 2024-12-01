from together import Together
from PIL import Image
import io
import base64
import os
import requests

client = Together()
# Update the debug print to check environment variable instead
print("API Key configured:", "TOGETHER_API_KEY" in os.environ)

response = client.images.generate(
    prompt="Cats eating popcorn",
    model="black-forest-labs/FLUX.1-schnell-Free",
    steps=2,
    n=1
)

# Print response to inspect its structure
print("Full API Response:", response)

# Download image from URL
image_url = response.data[0].url
print(image_url)

# Print clickable URL
print(f"\nImage URL (click to open in browser): {image_url}")

# Download image from URL
image_response = requests.get(image_url)
image = Image.open(io.BytesIO(image_response.content))

# Display the image
image.show()

# Optionally, save the image
# image.save("cats_eating_popcorn.png")