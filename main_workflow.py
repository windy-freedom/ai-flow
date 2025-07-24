import subprocess
import os
import sys
from datetime import datetime
import re
import argparse
import json

# --- Configuration ---
# Image generation parameters (using defaults and example prompt for testing)
# image_prompt = "men Dressing in white t shirt, full-body stand front view image :25, outdoor, Venice beach sign, full-body image, Los Angeles, Fashion photography of 90s, documentary, Film grain, photorealistic"
# For actual use, prompt will be generated from keywords.

# Video generation parameters
video_model = "MiniMax-Hailuo-02" # Default model
video_duration = 6 # User specified 6s
video_resolution = "768P" # User specified 768P

# Filename formats
current_date_str = datetime.now().strftime('%Y-%m-%d')
image_base_filename = f"{current_date_str}-ai-art"
video_base_filename = f"{current_date_str}-ai-art-video"

# --- Functions ---

def run_script(script_name, *args):
    """Runs a Python script using subprocess and captures its stdout."""
    command = [sys.executable, script_name] + list(args)
    print(f"Running command: {' '.join(command)}")
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"--- Output of {script_name} ---")
        print(process.stdout)
        if process.stderr:
            print(f"--- Errors from {script_name} ---")
            print(process.stderr)
        return process.stdout # Return stdout for parsing
    except FileNotFoundError:
        print(f"Error: Script '{script_name}' not found.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_name}: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while running {script_name}: {e}")
        return None

def extract_prompt_from_output(output):
    """Extracts the generated prompt from the stdout of prompt_generator.py."""
    if not output:
        return None
    
    # Find the content between PROMPT_OUTPUT_START and PROMPT_OUTPUT_END
    match = re.search(r"PROMPT_OUTPUT_START:(.*?):PROMPT_OUTPUT_END", output, re.DOTALL)
    if match:
        json_string = match.group(1)
        try:
            # The extracted content is the JSON string from prompt_generator.py
            output_json = json.loads(json_string)
            
            # Extract the content from the JSON structure.
            # The prompt is nested within choices -> message -> content.
            if 'choices' in output_json and output_json['choices']:
                message = output_json['choices'][0].get('message', {})
                content = message.get('content', '')
                
                # Extract only the actual prompt text from the content
                prompt_match = re.search(r"\*\*Prompt:\*\*\s*\"(.*?)\"", content, re.DOTALL)
                if prompt_match:
                    return prompt_match.group(1).strip()
                else:
                    # Fallback if the **Prompt:** format is not found
                    return content.strip()
                    
        except json.JSONDecodeError:
            print("Error: Could not decode JSON output from prompt_generator.py.")
        except KeyError as e:
            print(f"Error: Missing key in JSON output: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during prompt extraction: {e}")
            
    return None

def extract_image_path_from_output(output):
    """Extracts the generated image path from the stdout of minimax_image_generator.py."""
    if not output:
        return None
    
    match = re.search(r"IMAGE_OUTPUT_START:(.*?):IMAGE_OUTPUT_END", output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def main_workflow(keywords):
    print("Starting the automated content generation workflow...")

    # Step 1: Generate Prompt
    print("\n--- Step 1: Generating Prompt ---")
    prompt_output = run_script("prompt_generator.py", "--keywords", keywords)
    generated_prompt = extract_prompt_from_output(prompt_output)

    if not generated_prompt:
        print("Failed to generate prompt. Aborting workflow.")
        return

    print(f"Successfully generated prompt: {generated_prompt}")

    # Step 2: Generate Image
    print("\n--- Step 2: Generating Image ---")
    image_output = run_script("minimax_image_generator.py", "--prompt", generated_prompt, "--keyword", keywords)
    if not image_output:
        print("Image generation failed. Aborting workflow.")
        return

    generated_image_path = extract_image_path_from_output(image_output)
    if not generated_image_path:
        print("Failed to extract image path. Aborting workflow.")
        return
    print(f"Successfully generated image: {generated_image_path}")

    # Step 3: Generate Video
    print("\n--- Step 3: Generating Video ---")
    # The video generation script dynamically uses the first generated image
    # and the specified video parameters.
    # Pass the first generated image as input to the video generation script.
    if not run_script("minimax_video_generator.py", "--input_image", generated_image_path):
        print("Video generation failed. Aborting workflow.")
        return

    print("\n--- Workflow completed successfully! ---")
    print("Prompt, images, and video have been generated and saved.")

if __name__ == '__main__':
    # --- Argument Parsing for main_workflow.py ---
    parser = argparse.ArgumentParser(description="Orchestrates the content generation workflow.")
    parser.add_argument("--keywords", type=str, required=True, help="Comma-separated keywords for prompt generation.")
    
    args = parser.parse_args()
    keywords_input = args.keywords

    # Check if the necessary scripts exist
    if not os.path.exists("minimax_api_client.py"):
        print("Error: minimax_api_client.py not found. Please ensure it exists.")
        sys.exit(1)
    if not os.path.exists("minimax_image_generator.py"):
        print("Error: minimax_image_generator.py not found. Please ensure it exists.")
        sys.exit(1)
    if not os.path.exists("minimax_video_generator.py"):
        print("Error: minimax_video_generator.py not found. Please ensure it exists.")
        sys.exit(1)
    if not os.path.exists("prompt_generator.py"):
        print("Error: prompt_generator.py not found. Please ensure it exists.")
        sys.exit(1)
        
    main_workflow(keywords_input)
