import os
import re
import time
import requests
import replicate
from typing import Optional, Dict, Any, List, Callable
from utils import create_blank_image

def generate_image(
    storyboard: Dict[str, Any],
    characters: List[Dict[str, Any]],
    style: str,
    image_generator_func: Callable[[str], Optional[bytes]]
) -> Optional[bytes]:
    # Construct the prompt
    prompt = storyboard['description']
    
    enhanced_prompt = f"{prompt} | {style}"
    
    # Add character descriptions
    character_descriptions = []
  
    for character in characters:
        name_forms = [
            character['name'].split()[0],  # First name
            character['name'],  # Full name
            f"{character['name'].split()[0]}'s",  # First name possessive
            f"{character['name']}'s",  # Full name possessive
            f"{character['name'].split()[0]}'",  # First name possessive (alternative)
            f"{character['name']}'"  # Full name possessive (alternative)
        ]
        
        # Check if any non-bracketed form of the name is in the prompt
        if any(
            form.lower() in prompt.lower() and 
            f"{{{{{form.lower()}}}}}" not in prompt.lower()
            for form in name_forms
        ):
            desc = f"{character['name']}'s appearance: {character['ethnicity']} {character['gender']} {character['age']} {character['facial_features']} {character['body_type']} {character['hair_style']} {character['accessories']}"
            character_descriptions.append(desc)
        
    if character_descriptions:
        enhanced_prompt += " | " + " | ".join(character_descriptions)
    
    # Remove all bracketed content
    enhanced_prompt = re.sub(r'\{\{.*?\}\}', '', enhanced_prompt)
    
    return image_generator_func(enhanced_prompt)


def generate_and_download_images(
    storyboard_project: Dict[str, Any],
    story_dir: str,
    image_style: str,
    image_generator_func: Callable[[str], Optional[bytes]]
) -> List[str]:
    start_time = time.time()  # 记录开始时间
    
    image_files = []
    characters = storyboard_project['characters']
    
    for i, storyboard in enumerate(storyboard_project['storyboards']):
        image_content = generate_image(storyboard, characters, image_style, image_generator_func)
        if image_content:
            image_filename = os.path.join(story_dir, f"scene_{storyboard['scene_number']}.png")
            storyboard['image'] = image_filename
            try:
                with open(image_filename, 'wb') as f:
                    f.write(image_content)
                image_files.append(image_filename)
                print(f"Image saved for scene {storyboard['scene_number']}")
            except IOError as e:
                print(f"Failed to save image for scene {storyboard['scene_number']}: {e}")
                if i > 0:
                    storyboard['image'] = image_files[-1]  # Use the previous image
                else:
                    # For the first image, create a blank image
                    create_blank_image(image_filename)
                    storyboard['image'] = image_filename
                    image_files.append(image_filename)
        else:
            print(f"Failed to generate image for scene {storyboard['scene_number']}")
            if i > 0:
                storyboard['image'] = image_files[-1]  # Use the previous image
            else:
                # For the first image, create a blank image
                image_filename = os.path.join(story_dir, f"scene_{storyboard['scene_number']}.png")
                create_blank_image(image_filename)
                storyboard['image'] = image_filename
                image_files.append(image_filename)
    
    end_time = time.time()  
    execution_time = end_time - start_time  
    print(f"generate_and_download_images execution time: {execution_time:.2f} seconds")  
    
    return image_files

