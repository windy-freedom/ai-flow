import json
import os
from datetime import datetime
import argparse # Import argparse for command-line arguments
import requests # Keep requests for downloading images
from minimax_api_client import MinimaxAPIClient # Import the new API client

# --- Configuration ---
# API key will be handled by MinimaxAPIClient, no need to hardcode here.
image_generation_url = "https://api.minimaxi.com/v1/image_generation"

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Generate images using MiniMax API.")
parser.add_argument("--prompt", type=str, required=True, help="The prompt text for image generation.")
parser.add_argument("--keyword", type=str, required=True, help="Keyword to be used in the filename.") # Added argument for keyword
parser.add_argument("--model", type=str, default="image-01", help="The model to use for generation (default: image-01).")
parser.add_argument("--aspect_ratio", type=str, default="16:9", help="The aspect ratio of the image (default: 16:9).")
parser.add_argument("--response_format", type=str, default="url", help="The format of the response (default: url).")
parser.add_argument("--n", type=int, default=3, help="The number of images to generate (default: 3).")
parser.add_argument("--prompt_optimizer", type=bool, default=True, help="Whether to optimize the prompt (default: True).")

args = parser.parse_args()

prompt_text = args.prompt
keyword = args.keyword # Get keyword from arguments
model_name = args.model
aspect_ratio = args.aspect_ratio
response_format = args.response_format
num_images = args.n
prompt_optimizer = args.prompt_optimizer

# Initialize the API client
try:
    client = MinimaxAPIClient()
except ValueError as e:
    print(f"Error initializing Minimax API client: {e}")
    exit(1) # Exit if API client cannot be initialized

payload = {
  "model": model_name,
  "prompt": prompt_text,
  "aspect_ratio": aspect_ratio,
  "response_format": response_format,
  "n": num_images,
  "prompt_optimizer": prompt_optimizer
}

print("Generating image...")
try:
    response_data = client.post(image_generation_url, payload)
    
    # Corrected line to access image URLs
    if "data" in response_data and "image_urls" in response_data["data"]:
        print("Image generated successfully. Downloading and saving...")
        image_urls = response_data["data"]["image_urls"]
        
        # Define filename format: YYYY-MM-DD-keyword-sequence.jpg
        base_filename = f"{datetime.now().strftime('%Y-%m-%d')}-{keyword}" # Use keyword here
        
        for i, img_url in enumerate(image_urls):
            try:
                img_response = requests.get(img_url, stream=True)
                if img_response.status_code == 200:
                    # Construct filename with sequence number
                    filename = f"{base_filename}-{i+1:03d}.jpg"
                    filepath = os.path.join("d:/AI-image", filename) # Save in current directory
                    
                    with open(filepath, 'wb') as f:
                        for chunk in img_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Saved image to: {filepath}")
                    if i == 0: # Only output the first image path
                        print(f"IMAGE_OUTPUT_START:{filepath}:IMAGE_OUTPUT_END")
                else:
                    print(f"Failed to download image {i+1} from {img_url}. Status code: {img_response.status_code}")
            except Exception as e:
                print(f"Error saving image {i+1}: {e}")
    else:
        print(f"Image generation failed. Response: {response_data}")
except Exception as e:
    print(f"An error occurred during image generation API call: {e}")
