from TTS.api import TTS
import logging

logger: logging.Logger
logger = logging.getLogger(__file__)

class coqui_tts:

    def __init__(self, model_name, device="cpu"):
        self.model_name = model_name
        logger.info(f"Initializing coqui voice {model_name} on {device}")
        self.tts = TTS(model_name=self.model_name,
                       progress_bar=False).to(device)

    def tts(self, text):
        audio = self.tts.tts(text=text)
        duration_ms = 0.1 + len(audio)/22.050
        return (audio, duration_ms)
