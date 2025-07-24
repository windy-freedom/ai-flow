import requests
import json
import os
from datetime import datetime
import argparse # Import argparse for command-line arguments

url = "https://api.minimaxi.com/v1/image_generation"
api_key="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLljYHkuIMiLCJVc2VyTmFtZSI6IuWNgeS4gyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTQ2MDE5NjI0NjA4ODY2NjgwIiwiUGhvbmUiOiIxMzY5NDQwNjk4NyIsIkdyb3VwSUQiOiIxOTQ2MDE5NjI0NjAwNDc4MDcyIiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMDctMjMgMTY6Mjc6MjgiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.lbUPCtM7eUBlxb0UbalnXopl2JYSqwkZWBht3Z_aD3k9x6UNeHJun-MHig_Q2jtW1ZmQzFC84hFgNA67QouTe6cCX9ot5s53oXNkJ4wTR0EwnqFVnUsaqKAAYT-9Qeyxw_1AO86sG0JK5bqHG9ZL4jqa8ErQh6majLelHdb_OnoDRMB9wQTJQLX34DiV6I8u_sowCrCBeYqaU56LKm6V8pXg0Vhw5tQnQqCdSt3aKAy1UPzntBU03rBK7ypIn2Dkz7a9GpLmbFC3DZDQnNqba5DgLpQXkgW2aIcL5yWugMADz38cBHEOwRxYBQ04a5hi6GksoTPTGSky7hXNkSOWXw" # User's provided API key

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

payload = json.dumps({
  "model": model_name,
  "prompt": prompt_text,
  "aspect_ratio": aspect_ratio,
  "response_format": response_format,
  "n": num_images,
  "prompt_optimizer": prompt_optimizer
})
headers = {
  'Authorization': f'Bearer {api_key}',
  'Content-Type': 'application/json'
}

print("Generating image...")
response = requests.request("POST", url, headers=headers, data=payload)

# Print raw response text for debugging
print(f"Raw response text: {response.text}")

try:
    response_data = response.json()
    # Corrected line to access image URLs
    if response.status_code == 200 and "data" in response_data and "image_urls" in response_data["data"]:
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
except json.JSONDecodeError:
    print("Failed to decode JSON response. The response might not be in JSON format.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
