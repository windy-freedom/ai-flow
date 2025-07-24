import os
import time
import requests
import json
import base64
import argparse # Import argparse for command-line arguments

api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLljYHkuIMiLCJVc2VyTmFtZSI6IuWNgeS4gyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTQ2MDE5NjI0NjA4ODY2NjgwIiwiUGhvbmUiOiIxMzY5NDQwNjk4NyIsIkdyb3VwSUQiOiIxOTQ2MDE5NjI0NjAwNDc4MDcyIiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMDctMjMgMTY6Mjc6MjgiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.lbUPCtM7eUBlxb0UbalnXopl2JYSqwkZWBht3Z_aD3k9x6UNeHJun-MHig_Q2jtW1ZmQzFC84hFgNA67QouTe6cCX9ot5s53oXNkJ4wTR0EwnqFVnUsaqKAAYT-9Qeyxw_1AO86sG0JK5bqHG9ZL4jqa8ErQh6majLelHdb_OnoDRMB9wQTJQLX34DiV6I8u_sowCrCBeYqaU56LKm6V8pXg0Vhw5tQnQqCdSt3aKAy1UPzntBU03rBK7ypIn2Dkz7a9GpLmbFC3DZDQnNqba5DgLpQXkgW2aIcL5yWugMADz38cBHEOwRxYBQ04a5hi6GksoTPTGSky7hXNkSOWXw" # User's provided API key

# prompt = "YOUR_PROMPT_HERE" # 请在此输入生成视频的提示词文本内容
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
    url = "https://api.minimaxi.com/v1/video_generation"
    
    encoded_image = encode_image_to_base64(input_image_path)
    if not encoded_image:
        return None # Indicate failure

    payload_dict = {
      "model": model,
      "duration":6,
      "resolution":"1080P",
      "first_frame_image": f"data:image/jpeg;base64,{encoded_image}" # Assuming JPEG, adjust if needed
    }
    
    # Add prompt only if provided, as per the user's clarification that they want to use the image
    # and the automation plan suggesting prompt might be optional or handled differently.
    # However, the example snippet provided by the user *does* include a prompt.
    # Let's add it back, but make it optional or ask the user for it.
    # For now, let's use a default prompt if none is provided, or ask the user.
    # Based on the user's last response "我不知道", it's better to ask for a prompt.
    # For now, I will use a placeholder and ask the user for it.
    if video_prompt:
        payload_dict["prompt"] = video_prompt
    else:
        # If no prompt is provided, we might need to ask the user or use a default.
        # For now, let's use a placeholder and prompt the user later if needed.
        # The user's previous response was "我不知道" when asked for prompt.
        # Let's assume for now that a prompt is not strictly required if an image is provided.
        # However, the example snippet *did* include a prompt.
        # Let's add a placeholder and prompt the user for it.
        payload_dict["prompt"] = "A default prompt for video generation." # Placeholder prompt

    payload = json.dumps(payload_dict)
    
    headers = {
      'authorization': 'Bearer ' + api_key,
      'content-type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    
    try:
        response_data = response.json()
        if response.status_code == 200 and 'task_id' in response_data:
            task_id = response_data['task_id']
            print("视频生成任务提交成功，任务ID："+task_id)
            return task_id
        else:
            print(f"视频生成任务提交失败。响应: {response_data}")
            return None
    except json.JSONDecodeError:
        print("Failed to decode JSON response. The response might not be in JSON format.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during task submission: {e}")
        return None


def query_video_generation(task_id: str):
    url = "https://api.minimaxi.com/v1/query/video_generation?task_id="+task_id
    headers = {
      'authorization': 'Bearer ' + api_key
    }
    response = requests.request("GET", url, headers=headers)
    
    try:
        response_data = response.json()
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
    except json.JSONDecodeError:
        print("Failed to decode JSON response for status query.")
        return "", "Unknown"
    except Exception as e:
        print(f"An unexpected error occurred during status query: {e}")
        return "", "Unknown"


def fetch_video_result(file_id: str):
    print("---------------视频生成成功，下载中---------------")
    url = "https://api.minimaxi.com/v1/files/retrieve?file_id="+file_id
    headers = {
        'authorization': 'Bearer '+api_key,
    }

    response = requests.request("GET", url, headers=headers)
    
    try:
        response_data = response.json()
        if response.status_code == 200 and 'file' in response_data and 'download_url' in response_data['file']:
            download_url = response_data['file']['download_url']
            print("视频下载链接：" + download_url)
            
            # Use the confirmed output_file_name
            with open(output_file_name, 'wb') as f:
                # Download the video content
                video_response = requests.get(download_url, stream=True)
                if video_response.status_code == 200:
                    for chunk in video_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                    print("已下载在："+os.getcwd()+'/'+output_file_name)
                else:
                    print(f"Failed to download video from {download_url}. Status code: {video_response.status_code}")
        else:
            print(f"Failed to retrieve video download URL. Response: {response_data}")
    except json.JSONDecodeError:
        print("Failed to decode JSON response for file retrieval.")
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
