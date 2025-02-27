Based on OpenAI's Translator, supports manual subtitles and automatically generated subtitles.

## Installation

1. Create virtual environment `conda create -n youtube_translator python=3.9`
2. Activate the virtual environment `conda activate youtube_translator`
3. Install the necessary lib

```markdown
pip install youtube-transcript-api
pip install openai
```

## How to use

1. config.json
    - `api_key`: You can buy an API from [OpenAI API](https://platform.openai.com/api-keys).
    - `model`: Choose a model, you can find other models in [Document](https://platform.openai.com/docs/models#current-model-aliases).
    - `target_language`: Choose a target language.
    - `language_code`: The script will fetch a transcript from YouTube according to the given priority, e.g. ‘English’ > ‘German’ > ‘Japanese’. You can find more detail in [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api).
    - `num_lines_per_translation`: The number of lines per translation. Too long will slow down the translation speed, too short will make it difficult for the AI to understand the context well.
    - `save_transcripts`: Save the transcripts and translation in local folder.
    - `subtile_color`, `num_displayed_subtitles`: NOT IMPLEMENTED YET!
2. run `python main.py`

## Update

- Ver 1.0.0
    - Implemented the basic functionality of the translation script
- Ver 1.0.1
    - Re-edited the script structure to make it easier to read
    - Modified the system role prompt
    - Adjusted the output format of bilingual subtitles
    - Increased the translation output speed

## Potential issues

- The translation for manual subtitles is very good, but for **automatically generated subtitles**, there may be **sentence-to-sentence alignment issues** (which do not affect the quality of the translation).

## Demo
![Demonstration](/images/demo_v1.0.1.jpg)