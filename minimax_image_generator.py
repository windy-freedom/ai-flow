import requests
import json
import os
from datetime import datetime
import argparse # Import argparse for command-line arguments

url = "https://api.minimaxi.com/v1/image_generation"
api_key="YOUR_API_KEY" # 请替换为您的实际 API Key
# api_key 应该从环境变量或配置文件中获取，不应硬编码在代码中。
# 例如：
# import os
# api_key = os.getenv("MINIMAX_API_KEY")

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
