import os
import re
import json
from datetime import datetime
import datetime
from typing import List, Dict
from PIL import Image


STORY_TYPES = [
    "Scary",
    "Mystery",
    "Bedtime",
    "Interesting History",
    "Urban Legends",
    "Motivational",
    "Fun Facts",
    "Long Form Jokes",
    "Life Pro Tips",
    "Philosophy",
    "Love",
]

STORY_TYPE_HASHTAGS = {
    "Scary": "#scary",
    "Mystery": "#mystery",
    "Bedtime": "#bedtime",
    "Interesting History": "#history",
    "Urban Legends": "#urbanlegends",
    "Motivational": "#motivation",
    "Fun Facts": "#funfacts",
    "Long Form Jokes": "#joke",
    "Life Pro Tips": "#lifeprotips",
    "Philosophy": "#philosophy",
    "Love": "#love",
}

def create_resource_dir(script_dir, story_type, title):
    # Remove leading and trailing quotation marks and spaces
    clean_title = title.strip().strip('"')

    # Remove special characters and replace spaces with underscores
    clean_title = re.sub(r'[^\w\s-]', '', clean_title)
    clean_title = re.sub(r'[-\s]+', '_', clean_title)

    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(script_dir), "data")
    os.makedirs(data_dir, exist_ok=True)

    # Create a directory for the story type
    story_type_dir = os.path.join(data_dir, story_type)
    os.makedirs(story_type_dir, exist_ok=True)

    # Create a directory for this story
    story_dir = os.path.join(story_type_dir, clean_title)
    os.makedirs(story_dir, exist_ok=True)

    return story_dir

def call_openai_api(client, messages, max_retries=3):
    config = load_config()
    # Add a system message requesting JSON output
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=config['openai']['model'],
                temperature=config['openai']['temperature'],
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying... (Attempt {attempt + 2} of {max_retries})")
            else:
                print("Max retries reached. Unable to get a valid response.")
    return None


def create_empty_storyboard(title):
    return {
        "project_info": {
            "title": title,
            "user": "AI Generated",
            "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        },
        "storyboards": []
    }

def pick_story_type():
    print("Choose a story type:")
    for i, story_type in enumerate(STORY_TYPES, 1):
        print(f"{i}. {story_type}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(STORY_TYPES):
                return STORY_TYPES[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def pick_image_style():
    styles = ["photorealistic", "cinematic", "anime", "comic-book", "pixar-art"]
    print("Choose an image style:")
    for i, style in enumerate(styles, 1):
        print(f"{i}. {style}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(styles):
                return styles[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def convert_to_timestamped_subtitles(chinese_storyboard_project: Dict, scene_duration: int = 10) -> List[Dict]:
    timestamped_subtitles = []
    current_time = datetime.timedelta()

    for scene in chinese_storyboard_project['storyboards']:
        subtitles = scene['subtitles'].split('\n')
        time_per_subtitle = scene_duration / len(subtitles)

        for subtitle in subtitles:
            start_time = current_time
            end_time = current_time + datetime.timedelta(seconds=time_per_subtitle)

            timestamped_subtitles.append({
                'start_time': start_time.total_seconds(),
                'end_time': end_time.total_seconds(),
                'text': subtitle.strip()
            })

            current_time = end_time

    return timestamped_subtitles

def format_timedelta(seconds: float) -> str:
    td = datetime.timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def save_timestamped_subtitles(timestamped_subtitles: List[Dict], output_file: str) -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        for i, subtitle in enumerate(timestamped_subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{format_timedelta(subtitle['start_time'])} --> {format_timedelta(subtitle['end_time'])}\n")
            f.write(f"{subtitle['text']}\n\n")

def load_config(config_file='config.json'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), config_file)
    with open(config_path, 'r') as f:
        return json.load(f)

def create_blank_image(filename, width=720, height=1280):
    blank_image = Image.new('RGB', (width, height), color='black')
    blank_image.save(filename)
    print(f"Created blank image: {filename}")

def pick_voice_name():
    # alloy, echo, fable, onyx, nova, and shimmer
    voices = [
        "alloy",
        "echo",
        "fable",
        "onyx",
        "nova",
        "shimmer"
    ]
    print("Choose a voice:")
    for i, voice in enumerate(voices, 1):
        print(f"{i}. {voice}")

    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(voices):
                return voices[choice - 1]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
