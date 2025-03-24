import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

def make_call_with_retry(category: str, url, data = None, retries=3, delay=2):

    if "notion" in url:
        headers = {
            "Authorization": f'Bearer {os.getenv("notion_api_key")}',
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
    if "clockify" in url:
        headers = {
            "X-Api-Key": os.getenv("clockify_api_key"),
            "Content-Type": "application/json",
        }

    #if data != None:
    #    print(data)
    for attempt in range(1, retries + 1):
        try:
            print(f"Attempt to {category} at {url}. {attempt} of {retries}")
            # Main call logic
            match category:
                case "post":
                    response = requests.post(url, headers=headers, json=data)
                case "get":
                    response = requests.get(url, headers=headers)
                case "patch":
                    response = requests.patch(url, headers=headers, json=data)
                case _:
                    raise ValueError(f"Unknown category: {category}")

            # Return response if successful
            result = response.json()
            response.raise_for_status()
            return result

        except requests.exceptions.RequestException as e:
            print(f"RequestException on attempt {attempt}: {e}")
            print(f'json response: {result["message"]}')
            if attempt < retries:
                time.sleep(delay)  # Wait before retrying
            else:
                print("Exceeded maximum retries. Returning None.")
                return None
        except ValueError as e:
            print(f"ValueError: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None