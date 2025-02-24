# Youtube Translator
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
    - `api_key`: You can but an API from [OpenAI API](https://platform.openai.com/api-keys).
    - `model`: Choose a model, you can find other models in [Document](https://platform.openai.com/docs/models#current-model-aliases).
    - `target_language`: Choose a target language.
    - `language_code`: The script will fetch a transcript from YouTube according to the given priority, e.g. ‘English’ > ‘German’ > ‘Japanese’. You can find more detail in [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api).
    - `save_transcripts`: Save the transcripts and translation in local folder.
    - `subtile_color`, `num_displayed_subtitles`: NOT IMPLEMENTED YET!
2. run `python main.py`

## Potential issues

- **Talking-type videos shorter than 5 minutes perform well**, while long videos with excessive content may struggle to achieve sentence-to-sentence matching with the original text.
- OpenAI's API is billed based on the number of tokens; please use it cautiously for super long videos.

## Demo
![Demonstration](/images/demo.jpg)