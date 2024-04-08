import assemblyai as aai

from data import config

aai.settings.api_key = config.ASSEMBLYAI_TOKEN
config = aai.TranscriptionConfig(language_code='ru')
transcriber = aai.Transcriber(config=config)


async def transcribe(url):
    transcript = transcriber.transcribe(url)
    return transcript.text
