from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import time
import json
from translator import check_openai_api_key
from translator import extract_video_id
from translator import translate
from translator import align_output
from translator import save_transcripts

# load config.json
try:
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
except FileNotFoundError:
    print("Error: can't find config file.")
except json.JSONDecodeError:
    print("Error: incorrect JSON format.")

API_KEY = config['api_key']
LANGUAGE_CODE = config['language_code']
NUM_LINES_PER_TRANSLATION = config['num_lines_per_translation']
SAVE_TRANSCRIPT = config['save_transcripts']

while not check_openai_api_key(API_KEY):
    API_KEY = input(f"Re-enter your OpenAI API key: ")

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

    # retrieve the available transcripts
    # `TranscriptList` object which is iterable and provides methods to filter the list of transcripts for specific languages and types
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_transcript(LANGUAGE_CODE)
    # fetch subtitles, `TranscriptList` -> `Transcript`
    transcript = transcript.fetch()

    num_translations = len(transcript)//NUM_LINES_PER_TRANSLATION
    if len(transcript) < NUM_LINES_PER_TRANSLATION:
        NUM_LINES_PER_TRANSLATION = len(transcript)
    start_time = time.time() # record start time
    full_formatted_transcripts_list = [] # used for save transcripts
    full_translations_list = [] # used for save translations
    for i in range(num_translations + 1):
        if i < num_translations:
            formatted_transcript = "\n".join([
                f"[{item['start']:.2f}s - {(transcript[NUM_LINES_PER_TRANSLATION * i + index + 1]['start'] if NUM_LINES_PER_TRANSLATION * i + index + 1 < len(transcript) else item['start'] + item['duration']):.2f}s] {item['text'].replace(chr(10), ' ')}"
                for index, item in enumerate(transcript[NUM_LINES_PER_TRANSLATION * i:NUM_LINES_PER_TRANSLATION * (i+1)])
            ])
        else:
            formatted_transcript = "\n".join([
                f"[{item['start']:.2f}s - {(transcript[NUM_LINES_PER_TRANSLATION * i + index + 1]['start'] if NUM_LINES_PER_TRANSLATION * i + index + 1 < len(transcript) else item['start'] + item['duration']):.2f}s] {item['text'].replace(chr(10), ' ')}"
                for index, item in enumerate(transcript[NUM_LINES_PER_TRANSLATION * i:])
            ])

        # translate the formatted_transcript in batches
        if formatted_transcript.strip():  # avoid formatted_transcript is a empty string
            
            # print(f"Requesting translation, please wait a moment... \nHINT: a conversation-style video of about 10 minutes requires approximately 60 seconds of waiting time. \n")
            translation = translate(config, client, formatted_transcript)

            # format output
            formatted_transcript_lines = formatted_transcript.split("\n")
            translation_lines = translation.split("\n")

            aligned_output = align_output(formatted_transcript_lines, translation_lines)
                
            print(f"{aligned_output}")
            
            full_formatted_transcripts_list.append(formatted_transcript)
            full_translations_list.append(translation)
    
    end_time = time.time()  # record end time
    elapsed_time = end_time - start_time  # calculate run time

    full_formatted_transcripts = "\n".join(full_formatted_transcripts_list)
    full_translations = "\n".join(full_translations_list)

    if SAVE_TRANSCRIPT == True:
        save_transcripts(video_id, full_formatted_transcripts, full_translations)
        print(f"Transcripts saved in path 'saved_subtitles/{video_id}/'. \n" if SAVE_TRANSCRIPT else "")
    
    print(f"Time cost {elapsed_time:.2f}s. \n ")
