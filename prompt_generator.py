import requests
import json
import argparse
import sys

# --- Configuration ---
# Using the same API key as before
api_key = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLljYHkuIMiLCJVc2VyTmFtZSI6IuWNgeS4gyIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTQ2MDE5NjI0NjA4ODY2NjgwIiwiUGhvbmUiOiIxMzY5NDQwNjk4NyIsIkdyb3VwSUQiOiIxOTQ2MDE5NjI0NjAwNDc4MDcyIiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMDctMjMgMTY6Mjc6MjgiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.lbUPCtM7eUBlxb0UbalnXopl2JYSqwkZWBht3Z_aD3k9x6UNeHJun-MHig_Q2jtW1ZmQzFC84hFgNA67QouTe6cCX9ot5s53oXNkJ4wTR0EwnqFVnUsaqKAAYT-9Qeyxw_1AO86sG0JK5bqHG9ZL4jqa8ErQh6majLelHdb_OnoDRMB9wQTJQLX34DiV6I8u_sowCrCBeYqaU56LKm6V8pXg0Vhw5tQnQqCdSt3aKAy1UPzntBU03rBK7ypIn2Dkz7a9GpLmbFC3DZDQnNqba5DgLpQXkgW2aIcL5yWugMADz38cBHEOwRxYBQ04a5hi6GksoTPTGSky7hXNkSOWXw"

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

# Construct the prompt for the text API
# We want a short prompt for image generation based on keywords.
system_prompt_content = f"You are an AI assistant that generates concise and descriptive prompts for image generation based on user-provided keywords. Generate a short, creative, and descriptive prompt for image generation using the following keywords: {keywords}. The prompt should be suitable for an image generation model."

payload = {
  "model": text_model,
  # "tokens_to_generate": max_tokens, # Removed as it's not supported by the API
  "reply_constraints": {"sender_type": "BOT", "sender_name": "PromptBot"},
  "messages": [
    {
      "role": "system", # Changed from sender_type to role
      "name": "MiniMax AI", # Changed from sender_name to name
      "content": system_prompt_content # Changed from text to content
    },
    {
      "role": "user", # Changed from sender_type to role
      "name": "用户", # Changed from sender_name to name
      "content": f"Generate a short, creative, and descriptive prompt for image generation using the following keywords: {keywords}. The prompt should be suitable for an image generation model." # Explicitly asking for prompt generation
    }
  ],
  # Removed bot_setting as it's not in the user's example for this endpoint
  # "bot_setting": [
  #   {
  #     "bot_name": "PromptBot",
  #     "content": "You are an AI assistant that generates concise and descriptive prompts for image generation based on user-provided keywords. Generate a short, creative, and descriptive prompt for image generation using the following keywords: {keywords}. The prompt should be suitable for an image generation model."
  #   }
  # ]
}

headers = {
  "Authorization": f"Bearer {api_key}",
  "Content-Type": "application/json"
}

try:
    print("Generating prompt based on keywords...")
    response = requests.post("https://api.minimaxi.com/v1/text/chatcompletion_v2", headers=headers, json=payload)
    
    # Print raw response text for debugging
    print(f"Raw response text: {response.text}")

    try:
        response_data = response.json()
        # Check for success status code and the presence of choices/messages
        if response.status_code == 200 and "choices" in response_data and response_data["choices"]:
            generated_prompt = response_data["choices"][0]["message"]["content"] # Adjusted access based on typical chat completion response structure
            print(f"Generated Prompt: {generated_prompt}")
            # Output the raw JSON response to stdout so it can be captured by the calling script
            print(f"PROMPT_OUTPUT_START:{json.dumps(response_data)}:PROMPT_OUTPUT_END")
        else:
            print(f"Prompt generation failed. Response: {response_data}")
            # sys.exit(1) # Removed for debugging
    except json.JSONDecodeError:
        print("Failed to decode JSON response. The response might not be in JSON format.")
        # sys.exit(1) # Removed for debugging

except Exception as e:
    print(f"An error occurred during prompt generation API call: {e}")
    # sys.exit(1) # Removed for debugging
