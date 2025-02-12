import json
import re


def extract_and_parse_json2(response: str) -> dict:
    # Remove leading and trailing backticks and "json" tag if present
    cleaned_response = response.strip().strip("`").strip()
    if cleaned_response.startswith("json"):
        cleaned_response = cleaned_response[4:].strip()

    try:
        storyboard_data = json.loads(cleaned_response)
        return storyboard_data
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")


def extract_and_parse_json(response: str) -> dict:
    """
    Extracts JSON from a string response and attempts to parse it.

    Args:
    response (str): The full response string, potentially containing non-JSON text.

    Returns:
    dict: Parsed JSON data if successful, empty dict if failed.
    """
    # Find the JSON part of the response
    json_match = re.search(r"\{.*\}", response, re.DOTALL)

    if json_match:
        json_str = json_match.group()
        try:
            parsed_data = json.loads(json_str)
            print("Successfully parsed JSON data.")
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Failed to parse JSON: {json_str}")
    else:
        print("No JSON object found in the response")

    return {}


# Test the function
test_response1 = """Here's the detailed storyboard for the story "The Secret Mission of Sophie Scholl" in JSON format:

{
  "title": "The Secret Mission of Sophie Scholl",
  "scenes": [
    {
      "scene_number": 1,
      "description": "Sophie Scholl, a young German student, walks through the bustling streets of Munich in 1942."
    },
    {
      "scene_number": 2,
      "description": "Sophie meets with her brother Hans and their friend Christoph in a dimly lit café."
    }
  ]
}"""

test_response2 = """
{
  "title": "The Secret Mission of Sophie Scholl",
  "scenes": [
    {
      "scene_number": 1,
      "description": "Sophie Scholl, a young German student, walks through the bustling streets of Munich in 1942."
    },
    {
      "scene_number": 2,
      "description": "Sophie meets with her brother Hans and their friend Christoph in a dimly lit café."
    }
  ]
}"""

result = extract_and_parse_json(test_response1)
print(result)
