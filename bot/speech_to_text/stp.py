import assemblyai as aai

from data import config

aai.settings.api_key = config.ASSEMBLYAI_TOKEN
config = aai.TranscriptionConfig(language_code='ru')
transcriber = aai.Transcriber(config=config)


async def transcribe(url):
    """
    Транскрибирует аудиофайл по указанному URL.
    """
    transcript = transcriber.transcribe(url)
    return transcript.text
