import os
import time
import requests # Keep requests for downloading video content
import json
import base64
import argparse # Import argparse for command-line arguments
from minimax_api_client import MinimaxAPIClient # Import the new API client

# --- Configuration ---
# API key will be handled by MinimaxAPIClient, no need to hardcode here.
model = "MiniMax-Hailuo-02"

def encode_image_to_base64(image_path):
    """Encodes an image file to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None

def invoke_video_generation(input_image_path: str, video_prompt: str = None)->str:
    print("-----------------提交视频生成任务-----------------")
    video_generation_url = "https://api.minimaxi.com/v1/video_generation"
    
    encoded_image = encode_image_to_base64(input_image_path)
    if not encoded_image:
        return None # Indicate failure

    payload_dict = {
      "model": model,
      "duration":6,
      "resolution":"1080P",
      "first_frame_image": f"data:image/jpeg;base64,{encoded_image}" # Assuming JPEG, adjust if needed
    }
    
    if video_prompt:
        payload_dict["prompt"] = video_prompt
    else:
        payload_dict["prompt"] = "A default prompt for video generation." # Placeholder prompt

    # Initialize the API client inside the function to ensure it's ready
    try:
        client = MinimaxAPIClient()
    except ValueError as e:
        print(f"Error initializing Minimax API client: {e}")
        return None

    try:
        response_data = client.post(video_generation_url, payload_dict)
        
        if 'task_id' in response_data:
            task_id = response_data['task_id']
            print("视频生成任务提交成功，任务ID："+task_id)
            return task_id
        else:
            print(f"视频生成任务提交失败。响应: {response_data}")
            return None
    except Exception as e:
        print(f"An unexpected error occurred during task submission: {e}")
        return None


def query_video_generation(task_id: str):
    query_url = f"https://api.minimaxi.com/v1/query/video_generation?task_id={task_id}"
    
    # Initialize the API client inside the function to ensure it's ready
    try:
        client = MinimaxAPIClient()
    except ValueError as e:
        print(f"Error initializing Minimax API client: {e}")
        return "", "Unknown"

    try:
        response_data = client.get(query_url)
        status = response_data.get('status')
        if status == 'Preparing':
            print("...准备中...")
            return "", 'Preparing'
        elif status == 'Queueing':
            print("...队列中...")
            return "", 'Queueing'
        elif status == 'Processing':
            print("...生成中...")
            return "", 'Processing'
        elif status == 'Success':
            return response_data.get('file_id'), "Finished"
        elif status == 'Fail':
            return "", "Fail"
        else:
            return "", "Unknown"
    except Exception as e:
        print(f"An unexpected error occurred during status query: {e}")
        return "", "Unknown"


def fetch_video_result(file_id: str):
    print("---------------视频生成成功，下载中---------------")
    retrieve_url = f"https://api.minimaxi.com/v1/files/retrieve?file_id={file_id}"
    
    # Initialize the API client inside the function to ensure it's ready
    try:
        client = MinimaxAPIClient()
    except ValueError as e:
        print(f"Error initializing Minimax API client: {e}")
        return

    try:
        response_data = client.get(retrieve_url)
        if 'file' in response_data and 'download_url' in response_data['file']:
            download_url = response_data['file']['download_url']
            print("视频下载链接：" + download_url)
            
            # Use the confirmed output_file_name
            with open(output_file_name, 'wb') as f:
                # Download the video content using requests directly as MinimaxAPIClient doesn't handle binary streams
                video_response = requests.get(download_url, stream=True)
                if video_response.status_code == 200:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                    print("已下载在："+os.getcwd()+'/'+output_file_name)
                else:
                    print(f"Failed to download video from {download_url}. Status code: {video_response.status_code}")
        else:
            print(f"Failed to retrieve video download URL. Response: {response_data}")
    except Exception as e:
        print(f"An unexpected error occurred during video download: {e}")


if __name__ == '__main__':
    # --- Argument Parsing for minimax_video_generator.py ---
    parser = argparse.ArgumentParser(description="Generate video using MiniMax API with an input image.")
    parser.add_argument("--input_image", type=str, required=True, help="Path to the input image file for video generation.")
    parser.add_argument("--video_prompt", type=str, default="A default prompt for video generation.", help="Optional prompt for video generation.")
    
    args = parser.parse_args()
    
    # Construct the output filename based on the input image name
    input_image_path_arg = args.input_image
    base_name = os.path.basename(input_image_path_arg)
    name_without_ext, _ = os.path.splitext(base_name)
    output_file_name = f"{name_without_ext}-video.mp4" # Construct the new output filename
    
    # Call invoke_video_generation with the provided image path and prompt
    task_id = invoke_video_generation(args.input_image, args.video_prompt)
    
    if task_id:
        print("-----------------已提交视频生成任务-----------------")
        while True:
            time.sleep(10) # Wait for 10 seconds before querying status

            file_id, status = query_video_generation(task_id)
            
            if status == "Finished" and file_id:
                fetch_video_result(file_id)
                print("---------------生成成功---------------")
                break
            elif status == "Fail" or status == "Unknown":
                print("---------------生成失败---------------")
                break
            # Continue loop if status is Preparing, Queueing, or Processing
    else:
        print("Failed to submit video generation task.")
