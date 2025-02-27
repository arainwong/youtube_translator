from openai import OpenAI, OpenAIError, AuthenticationError
from youtube_transcript_api import YouTubeTranscriptApi
import re
import os

def check_openai_api_key(api_key: str) -> bool:
    """
    Check whether the OpenAI API Key is valid without affecting the main application's OpenAI client.
    """
    try:
        temp_client = OpenAI(api_key=api_key)  # create temporary client
        completion = temp_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "This is a message to test client connection."}]
        )
        return True  # valid API Key
    except AuthenticationError:
        print("API Key authentication failed: Invalid API Key \n")
        return False
    except OpenAIError as e:
        print(f"Other OpenAI error: {e} \n")
        return False  # may be a network issue, request format error, etc
    finally:
        del temp_client  # delete the temporary client to prevent contamination to main client

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

def translate(config, client, formatted_transcript: str):
    '''
    Query OpenAI to translate.
    '''

    MODEL = config['model']
    TARGET_LANGUAGE = config['target_language']

    ROLL_PROMPT = "\n".join([f"你是一位出色的翻译官，请将以下内容翻译成{TARGET_LANGUAGE}，有以下要求： \n 1. 内容可能较多，将分批次发送给你，但请严格以相同的格式进行翻译，原文中有几行请你也翻译成几行。\n 2. 内容中的一些单词 可能出于与前后词语发音相似的原因 而被记录成错误的单词，请你帮忙联想成与前后文相符的单词并加以纠正。 \n 3. 要求句子通畅，对于潜在的术语以及人名请保留原文。"])

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
    # Regular expression filtering line break conditions: since Chinese is used here, "。" is used as the line break condition.
    # translation = re.sub(r'(?<=。)(?=[^\n])', '\n', translation)  # add "\n" after "。"
    translation = re.sub(r'\n+', '\n', translation).strip()  # remove extra blank lines

    return translation

def format_time(seconds):
    """ Convert seconds to mm:ss format """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"  # mm:ss

def align_output(formatted_transcript_lines: list, translation_lines: list):
    """
    Output:
        original text
        translated text

        original text
        translated text

        ...
    """
    # match the number of lines
    min_lines = min(len(formatted_transcript_lines), len(translation_lines))
    max_lines = max(len(formatted_transcript_lines), len(translation_lines))
    
    # line-by-line concatenation of the corresponding translation
    aligned_output1 = "\n".join(
        [f"{formatted_transcript_lines[i]}\n{translation_lines[i]}\n" for i in range(min_lines)]
    )

    if len(formatted_transcript_lines) > len(translation_lines):
        aligned_output2 = "\n".join([f"{formatted_transcript_lines[i]}\n" for i in range(min_lines, max_lines)])
    else:
        aligned_output2 = "\n".join([f"{translation_lines[i]}\n" for i in range(min_lines, max_lines)])

    # ensure there is only one '\n' at the end
    aligned_output = f"{aligned_output1}\n{aligned_output2}".strip() + "\n"

    return aligned_output


def save_transcripts(video_id: str, full_formatted_transcripts: str, full_translations: str):
    # set the save path, if not exist then create a new folder
    save_path = f'saved_subtitles/{video_id}/'
    os.makedirs(save_path, exist_ok=True)
    # write transcript to 'TRANSCRIPT.txt' file
    with open(os.path.join(save_path, 'original_transcript.txt'), 'w', encoding='utf-8') as txt_file:
        txt_file.write(full_formatted_transcripts)
    with open(os.path.join(save_path, 'translated_transcript.txt'), 'w', encoding='utf-8') as txt_file:
        txt_file.write(full_translations)


####################################################################################
####################################################################################
####################################################################################

def translate_deprecated_v1(config, video_id: str, client):
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