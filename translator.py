# from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os

def extract_video_id(url):
    '''
    Extract YouTube video ID.
    Available for both of URL and video ID.
    '''
    if len(url) > 11:
        match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
        return match.group(1) if match else None
    elif len(url) == 11:
        return url
    else:
        return None
    

def translate(config, video_id, client):
    '''
    Query OpenAI to translate.

    Input:
        - config: configuration file, here indicate 'config.json'
        - video_id: YouTube video ID
        - client: OpenAI client
    Output:
        - formatted_transcript_lines: formatted subtitles
        - translation_lines: formatted translated subtitles
    '''

    MODEL = config['model']
    TARGET_LANGUAGE = config['target_language']
    LANGUAGE_CODE = config['language_code']
    SAVE_TRANSCRIPT = config['save_transcripts']

    ROLL_PROMPT = "\n".join([f"你是一位出色的翻译官，请将以下'text'中的内容翻译成{TARGET_LANGUAGE}并同时原有的文本格式。此外，'text'中的一些单词可能因为发音相似的原因而被记录成错误的单词，请你帮忙联想成与前后文相符的单词并加以纠正。要求句子通畅，对于可能的人名请翻译成英文名。"])


    # retrieve the available transcripts
    # `TranscriptList` object which is iterable and provides methods to filter the list of transcripts for specific languages and types
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_transcript(LANGUAGE_CODE)
    # fetch subtitles, `TranscriptList` -> `Transcript`
    transcript = transcript.fetch()

    # format transcript to, e.g. "[0.08s - 5.12s] TextsTextsTextsTexts..."
    formatted_transcript = "\n".join([
        f"[{item['start']:.2f}s - {item['start'] + item['duration']:.2f}s] {item['text'].replace(chr(10), ' ')}"
        for item in transcript
    ])

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ROLL_PROMPT},
            {
                "role": "user",
                "content": formatted_transcript
            }
        ]
    )

    translation = completion.choices[0].message.content
    # Regular expression filtering line break conditions: 
    # since Chinese is used here, "。" is used as the line break condition.
    translation = re.sub(r'(?<=。)(?=[^\n])', '\n', translation)  # add "\n" after "。"
    translation = re.sub(r'\n+', '\n', translation).strip()  # remove extra blank lines

    if SAVE_TRANSCRIPT == True:
        # set the save path, if not exist then create a new folder
        save_path = f'saved_subtitles/{video_id}/'
        os.makedirs(save_path, exist_ok=True)
        # write transcript to 'TRANSCRIPT.txt' file
        with open(os.path.join(save_path, 'original_transcript.txt'), 'w', encoding='utf-8') as txt_file:
            txt_file.write(formatted_transcript)
        with open(os.path.join(save_path, 'translated_transcript.txt'), 'w', encoding='utf-8') as txt_file:
            txt_file.write(translation)

    # format output
    formatted_transcript_lines = formatted_transcript.split("\n")
    translation_lines = translation.split("\n")

    return formatted_transcript_lines, translation_lines