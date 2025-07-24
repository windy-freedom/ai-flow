import json
import argparse
import sys
from minimax_api_client import MinimaxAPIClient # Import the new API client

# --- Configuration ---
# API key will be handled by MinimaxAPIClient, no need to hardcode here.

# --- Argument Parsing ---
parser = argparse.ArgumentParser(description="Generate a short prompt for image generation using MiniMax API.")
parser.add_argument("--keywords", type=str, required=True, help="Comma-separated keywords to generate a prompt from.")
# Using the model specified in the user's example code
parser.add_argument("--model", type=str, default="MiniMax-M1", help="The text generation model to use (default: MiniMax-M1).")
parser.add_argument("--max_tokens", type=int, default=50, help="Maximum number of tokens for the generated prompt (default: 50).") # User preference for "short" prompt

args = parser.parse_args()

keywords = args.keywords
text_model = args.model
max_tokens = args.max_tokens

# Initialize the API client
try:
    client = MinimaxAPIClient()
except ValueError as e:
    print(f"Error initializing Minimax API client: {e}")
    sys.exit(1)

# Construct the prompt for the text API
# We want a short prompt for image generation based on keywords.
system_prompt_content = f"You are an AI assistant that generates concise and descriptive prompts for image generation based on user-provided keywords. Generate a short, creative, and descriptive prompt for image generation using the following keywords: {keywords}. The prompt should be suitable for an image generation model."

payload = {
  "model": text_model,
  "reply_constraints": {"sender_type": "BOT", "sender_name": "PromptBot"},
  "messages": [
    {
      "role": "system",
      "name": "MiniMax AI",
      "content": system_prompt_content
    },
    {
      "role": "user",
      "name": "用户",
      "content": f"Generate a short, creative, and descriptive prompt for image generation using the following keywords: {keywords}. The prompt should be suitable for an image generation model."
    }
  ],
}

try:
    print("Generating prompt based on keywords...")
    response_data = client.post("https://api.minimaxi.com/v1/text/chatcompletion_v2", payload)
    
    # Print raw response text for debugging (if needed, client.post already prints errors)
    # print(f"Raw response text: {json.dumps(response_data)}")

    # Check for success status code and the presence of choices/messages
    if "choices" in response_data and response_data["choices"]:
        generated_prompt = response_data["choices"][0]["message"]["content"]
        print(f"Generated Prompt: {generated_prompt}")
        # Output the raw JSON response to stdout so it can be captured by the calling script
        print(f"PROMPT_OUTPUT_START:{json.dumps(response_data)}:PROMPT_OUTPUT_END")
    else:
        print(f"Prompt generation failed. Response: {response_data}")
except Exception as e:
    print(f"An error occurred during prompt generation API call: {e}")
    sys.exit(1)
