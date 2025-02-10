import os
from dotenv import load_dotenv
from utils import load_config

load_dotenv()

def generate_audio(client, text, output_file, voice_name):
    config = load_config()
    # Get the speech rate from the config file
    speech_rate = config['tts']['speech_rate']

    try:
        result = client.audio.speech.create(
            model="tts-1",
            voice=voice_name,
            input=text,
            speed=speech_rate,
            response_format="mp3"
        )

        # Save the audio content to the output file
        with open(output_file, "wb") as audio_file:
            audio_file.write(result.content)

        print(f"Speech synthesized for text [{text}], and the audio was saved to [{output_file}]")
        return True

    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        return False
