import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from video_creator import create_video
from api import replicate_flux_api, fal_flux_api
from utils import pick_story_type, pick_image_style, pick_voice_name, load_config
from story_generator import (
    generate_general_storyboard,
    generate_life_pro_tips_storyboard,
    generate_characters,
    generate_philosophy_storyboard,
    generate_fun_facts_storyboard,
)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the .env file
dotenv_path = os.path.join(os.path.dirname(script_dir), ".env")
# Load the .env file
load_dotenv(dotenv_path)

local_config = load_config()
# Initialize the OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


def test_text_to_image(script_dir):
    # 1. pick story type, image style and voice name
    story_type = pick_story_type()
    image_style = pick_image_style()

    # story dir is in the data/Samples
    story_dir = os.path.join(script_dir, "../data/Images")

    title, story = None, None
    # read the story from file
    with open(
        os.path.join(script_dir, story_dir, "story_english.txt"), "r", encoding="utf-8"
    ) as f:
        content = f.read()
        title, story = content.split("\n\n", 1)

    characters = []
    if story_type.lower() != "life pro tips" and story_type.lower() != "fun facts":
        print("\nGenerating character descriptions...")
        characters = generate_characters(client, story)
        if characters is None:
            print("Failed to generate characters. Please try again later.")
            return
        print("characters: ", characters)

    character_names = (
        [character["name"] for character in characters] if characters else []
    )

    # generate storyboard
    print("\nGenerating storyboard...")
    if story_type.lower() == "life pro tips":
        storyboard_project = generate_life_pro_tips_storyboard(client, title, story)
    elif story_type.lower() == "philosophy":
        storyboard_project = generate_philosophy_storyboard(
            client, title, story, character_names
        )
    elif story_type.lower() == "fun facts":
        storyboard_project = generate_fun_facts_storyboard(client, title, story)
    else:
        storyboard_project = generate_general_storyboard(
            client, title, story, character_names
        )

    if len(storyboard_project.get("storyboards")) == 0:
        print("Failed to generate storyboard. Please try again later.")
        return
    storyboard_project["characters"] = characters

    # generate images and download images
    from image_generator import generate_and_download_images

    image_files = generate_and_download_images(
        storyboard_project, story_dir, image_style, fal_flux_api
    )
    print(image_files)

    # Save the storyboard_project to a json file
    print("\nSaving storyboard project...")
    with open(
        os.path.join(script_dir, story_dir, "storyboard_project.json"),
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(storyboard_project, f, ensure_ascii=False, indent=4)


def test_video_from_images(script_dir):
    voice_name = pick_voice_name()
    # Set up the directory paths
    audio_dir = os.path.join(story_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    video_path = os.path.join(story_dir, "story_video.mp4")

    # Load the storyboard project
    with open(
        os.path.join(story_dir, "storyboard_project.json"), "r", encoding="utf-8"
    ) as f:
        storyboard_project = json.load(f)

    # Get all .webp image files in the directory
    print("\nCreating video from images...")
    create_video(client, storyboard_project, video_path, audio_dir, voice_name)

    print(f"Video created: {video_path}")


if __name__ == "__main__":
    test_text_to_image(script_dir)
    # test_video_from_images(script_dir)
