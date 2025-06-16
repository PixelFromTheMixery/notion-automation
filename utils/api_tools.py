from utils.logger import logger

import os, requests, time
from dotenv import load_dotenv
import base64

load_dotenv()

def make_call_with_retry(
    category: str,
    url,
    info,
    data=None,
    retries=3,
    delay=2,
):
    if "notion" in url:
        headers = {
            "Authorization": f'Bearer {os.getenv("notion_key")}',
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }
    elif "trackingtime" in url:
        auth_raw = f"aya.b.jackson@gmail.com:{os.getenv('ttime_key')}"
        ttime_key_b64 = base64.b64encode(auth_raw.encode()).decode()

        headers= {
            "Authorization": f'Basic ' + ttime_key_b64,
            "Content-Type": "application/json"
        }

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Attempt to {info}. {attempt} of {retries}")
            
            match category:
                case "get":
                    response = requests.get(url, headers=headers)
                case "patch":
                    response = requests.patch(url, headers=headers, json=data)
                case "post":
                    response = requests.post(url, headers=headers, json=data)
                case "put":
                    response = requests.put(url, headers=headers, json=data)
                case _:
                    raise ValueError(f"Unknown category: {category}")

            result = response.json()
            response.raise_for_status()
            if "results" in result:
                return result["results"]
            else:
                return result

        except requests.exceptions.RequestException as e:
            print(f"RequestException on attempt {attempt}: {e}")
            print(f'json response: {result["message"]}')
            if "not a property that exists" in result["message"]:
                raise ValueError("Property does not exist, will attempt match")
            if attempt < retries:
                time.sleep(delay)
            else:
                raise Exception(f"Request failed: {e}") from e
        except ValueError as e:
            print(f"ValueError: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
