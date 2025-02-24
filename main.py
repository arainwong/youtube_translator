# from youtube_transcript_api import YouTubeTranscriptApi
# import re
from openai import OpenAI
import time
import json
from translator import extract_video_id
from translator import translate

# load config.json
try:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
except FileNotFoundError:
    print("Error: can't find config file.")
except json.JSONDecodeError:
    print("Error: incorrect JSON format.")

API_KEY = config['api_key']
SAVE_TRANSCRIPT = config['save_transcripts']
client = OpenAI(api_key=API_KEY)

while True:
    # get video ID
    url = input("Enter a YouTube URL or video ID (\"exit\" to stop): ") 
    if url.lower() == "exit":
        break
    video_id = extract_video_id(url)
    if video_id is None:
        print(f"Invalid URL or video ID. Try again.")
        continue
    else:
        print(f"\nSuccessfully extract video ID: {video_id} \n")
    
    # fetch the manual or generated subtitles and translate to target language
    start_time = time.time() # record start time
    print(f"Requesting translation, please wait a moment... \nHINT: a conversation-style video of about 10 minutes requires approximately 60 seconds of waiting time. \n")
    formatted_transcript_lines, translation_lines = translate(config=config, video_id=video_id, client=client)
    end_time = time.time()  # record end time
    elapsed_time = end_time - start_time  # calculate run time

    # match the number of lines
    min_lines = min(len(formatted_transcript_lines), len(translation_lines))
    max_lines = max(len(formatted_transcript_lines), len(translation_lines))

    # line-by-line concatenation of the corresponding translation
    aligned_output1 = "\n".join([f"{formatted_transcript_lines[i]} \n{translation_lines[i]} \n" for i in range(min_lines)])
    if len(formatted_transcript_lines) >= len(translation_lines):
        aligned_output2 = "\n".join([f"{formatted_transcript_lines[i]} \n" for i in range(min_lines, max_lines)])
    else:
        aligned_output2 = "\n".join([f"{translation_lines[i]} \n" for i in range(min_lines, max_lines)])
        
    print(f"{aligned_output1} \n{aligned_output2}")
    print(f"Time cost {elapsed_time:.2f}s.")
    print(f"Transcripts saved in path 'saved_subtitles/{video_id}/'. \n" if SAVE_TRANSCRIPT else "")
