import requests
import json
import os
from config import MINIMAX_API_KEY # Import API key from config.py

class MinimaxAPIClient:
    def __init__(self, api_key=None):
        # Prioritize passed api_key, then config.py, then environment variable
        self.api_key = api_key if api_key else MINIMAX_API_KEY
        if not self.api_key:
            raise ValueError("Minimax API key not found. Please set MINIMAX_API_KEY in config.py or as an environment variable, or pass it during initialization.")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def post(self, url, payload):
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.text}")
            raise
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Error connecting to Minimax API: {conn_err}")
            raise
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error: {timeout_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred during the request: {req_err}")
            raise
        except json.JSONDecodeError:
            print("Failed to decode JSON response from API.")
            print(f"Raw response text: {response.text}")
            raise

    def get(self, url, params=None):
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            print(f"Response content: {response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred during the request: {req_err}")
            raise
        except json.JSONDecodeError:
            print("Failed to decode JSON response from API.")
            print(f"Raw response text: {response.text}")
            raise

# Example usage (for testing purposes, not part of the main client)
if __name__ == '__main__':
    # For testing, you might temporarily set the API key here or ensure it's in your environment
    # os.environ["MINIMAX_API_KEY"] = "YOUR_ACTUAL_API_KEY"
    try:
        # When running this example, it will try to get the key from config.py first, then env.
        client = MinimaxAPIClient()
        print("MinimaxAPIClient initialized successfully.")
        # You can add a simple test call here if you have a test endpoint
        # For example, a dummy call to a non-existent endpoint to test error handling
        # client.post("https://api.minimaxi.com/v1/test_endpoint", {"data": "test"})
    except ValueError as e:
        print(f"Initialization error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during client initialization: {e}")
