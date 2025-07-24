import argparse
import subprocess
import os
import json
import sys
import re
from datetime import datetime

def run_command(command):
    """Helper function to run shell commands and print output, capturing stderr."""
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout_output = []
    stderr_output = []

    for line in process.stdout:
        print(line, end='')
        stdout_output.append(line)
    
    for line in process.stderr:
        print(line, end='')
        stderr_output.append(line)

    process.wait()
    return "".join(stdout_output), "".join(stderr_output), process.returncode

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
                prompt_match = re.search(r"\*\*Prompt:\*\*\s*(.*?)(?:\n|$)", content, re.DOTALL)
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
    prompt_stdout, prompt_stderr, return_code = run_command(f"python prompt_generator.py --keywords \"{keywords}\"")
    
    if return_code != 0:
        print(f"Failed to generate prompt. Aborting workflow. Stderr: {prompt_stderr}")
        return

    generated_prompt = extract_prompt_from_output(prompt_stdout)

    if not generated_prompt:
        print("Failed to extract generated prompt from output. Aborting workflow.")
        return

    print(f"Successfully generated prompt: {generated_prompt}")

    # Step 2: Generate Image
    print("\n--- Step 2: Generating Image ---")
    image_stdout, image_stderr, return_code = run_command(f"python minimax_image_generator.py --prompt \"{generated_prompt}\" --keyword \"{keywords}\"")
    
    if return_code != 0:
        print(f"Image generation failed. Aborting workflow. Stderr: {image_stderr}")
        return

    generated_image_path = extract_image_path_from_output(image_stdout)
    if not generated_image_path:
        print("Failed to extract image path. Aborting workflow.")
        return
    print(f"Successfully generated image: {generated_image_path}")

    # Step 3: Generate Video
    print("\n--- Step 3: Generating Video ---")
    video_stdout, video_stderr, return_code = run_command(f"python minimax_video_generator.py --input_image \"{generated_image_path}\"")
    
    if return_code != 0:
        print(f"Video generation failed. Stderr: {video_stderr}")
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
