"""
Product Creator Script
---------------------
This script generates product listings by:
1. Reading product details from input.csv
2. Generating titles, descriptions, and tags using Mistral AI
3. Creating images using Together AI
4. Saving results to product_information.csv

Required Environment Variables:
- MISTRAL_API_KEY: Your Mistral AI API key
- TOGETHER_API_KEY: Your Together AI API key

Required Files:
- input.csv: Must contain a 'details' column with product themes/descriptions
"""

import os
import pandas as pd
from tqdm import tqdm
from PIL import Image
import requests
import io
from together import Together
import time

class MistralAPI:
    """Handles all interactions with the Mistral AI API"""
    
    def __init__(self, api_key):
        """Initialize the Mistral API client
        
        Args:
            api_key (str): Mistral API authentication key
        """
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.max_retries = 3
        self.retry_delay = 2
        self.timeout = 30

    def _make_request(self, prompt):
        """Make a request to Mistral API with retry logic
        
        Args:
            prompt (str): The prompt to send to the API
            
        Returns:
            str: The API response content
            
        Raises:
            Exception: If all retry attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-tiny",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ]
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', self.retry_delay * (attempt + 1)))
                    print(f"Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                return response.json()['choices'][0]['message']['content'].strip()
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"Error: {str(e)}. Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    continue
                raise

    def generate_title(self, detail):
        """Generate a product title
        
        Args:
            detail (str): Product theme/description
            
        Returns:
            str: Generated title
        """
        print("Generating title...")
        prompt = f"Generate a catchy title with theme: '{detail}'. Max 50 chars.'"
        return self._make_request(prompt).replace('"', '')

    def generate_description(self, detail, title):
        """Generate a product description based on title
        
        Args:
            detail (str): Product theme/description
            title (str): Generated product title
            
        Returns:
            str: Generated description with appended template
        """
        print("Generating description...")
        prompt = f"""Generate a compelling description for a product with:
        Title: {title}
        Theme: {detail}
        Maximum 150 characters."""
        
        description = self._make_request(prompt).replace('"', '')
        return description + self._get_template_description()

    def generate_image_prompt(self, detail):
        """Generate an image creation prompt
        
        Args:
            detail (str): Product theme/description
            
        Returns:
            str: Generated image prompt
        """
        print("Generating image prompt...")
        prompt = f"Generate a creative image prompt for a T-shirt with theme: '{detail}'. Max 75 chars."
        return self._make_request(prompt).replace('"', '')

    def generate_tags(self, detail):
        """Generate product tags
        
        Args:
            detail (str): Product theme/description
            
        Returns:
            str: Comma-separated tags
        """
        print("Generating tags...")
        prompt = f"Generate relevant tags for a T-shirt with theme: '{detail}'. Separate with commas."
        return self._make_request(prompt).replace('"', '')

    @staticmethod
    def _get_template_description():
        """Returns the template description for all products"""
        return """
        <p>Acrylic art panels are a modern way to display beautiful and vibrant art that looks like it's embedded in clear glass. 
        They have a clear, glossy acrylic surface and a white vinyl backing. Four silver stand-offs make it very easy to mount to the wall.</p>
        <p>.: Material: Clear acrylic with white vinyl backing<br />
        .: Clear, glossy surface<br />
        .: Seven sizes to choose from<br />
        .: Horizontal, vertical and square options available<br />
        .: NB! For indoor use only</p>
        """

def generate_image(client, prompt):
    """Generate an image using Together AI
    
    Args:
        client: Together AI client
        prompt (str): Image generation prompt
        
    Returns:
        tuple: (PIL.Image, str) The generated image and its URL
    """
    print("Generating image...")
    try:
        response = client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            steps=2,
            n=1
        )
        
        image_url = response.data[0].url
        print(f"Image URL: {image_url}")
        
        image_response = requests.get(image_url)
        return Image.open(io.BytesIO(image_response.content)), image_url
        
    except Exception as e:
        print(f"Error generating image: {e}")
        return None, None

def main():
    """Main execution function"""
    # Validate environment variables
    mistral_api_key = os.getenv('MISTRAL_API_KEY')
    if not mistral_api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set")

    # Initialize APIs
    mistral = MistralAPI(mistral_api_key)
    together_client = Together()

    # Process input file
    try:
        df = pd.read_csv("input.csv")
    except FileNotFoundError:
        raise FileNotFoundError("input.csv not found in current directory")
    except pd.errors.EmptyDataError:
        raise ValueError("input.csv is empty")

    if 'details' not in df.columns:
        raise ValueError("input.csv must contain a 'details' column")

    # Initialize result storage
    results = {
        "file_name": [],
        "local_path": [],
        "title": [],
        "description": [],
        "tags": []
    }

    # Process each row
    for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing products"):
        detail = row['details']
        
        # Generate content
        title = mistral.generate_title(detail)
        print(f"Title: {title}")
        description = mistral.generate_description(detail, title)
        print(f"Description: {description}")
        image_prompt = mistral.generate_image_prompt(detail)
        print(f"Image prompt: {image_prompt}")
        tags = mistral.generate_tags(detail)
        print(f"Tags: {tags}")

        # Generate and save image
        image, image_url = generate_image(together_client, image_prompt)
        if image:
            file_name = f"image_{idx}.png"
            image.save(file_name)
            
            # Store results
            results["file_name"].append(file_name)
            results["local_path"].append(file_name)
            results["title"].append(title)
            results["description"].append(description)
            results["tags"].append(tags)

    # Save results
    output_df = pd.DataFrame(results)
    output_df.to_csv("product_information.csv", index=False)
    print(f"Results saved to product_information.csv")

if __name__ == "__main__":
    main()
