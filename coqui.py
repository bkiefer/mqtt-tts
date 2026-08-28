from TTS.api import TTS
import logging

logger: logging.Logger
logger = logging.getLogger(__file__)

class coqui_tts:

    def __init__(self, config):
        device = config.get("device", "cpu")
        red_conf = {k: config[k] for k in ['model_name',
                                           'vocoder_path', 'vocoder_config_path',
                                           'model_path', 'config_path']
                                 if k in config}
        red_conf['progress_bar'] = False

        name = red_conf.get('model_name') or red_conf.get('model_path')
        logger.info(f"Initializing coqui voice {name} on {device}")
        self.model = TTS(**red_conf).to(device)

    def tts(self, text):
        audio = self.model.tts(text=text)
        duration_ms = 0.1 + len(audio)/22.050
        return (audio, duration_ms)

if __name__ == '__main__':
    #import os
    #os.environ['TTS_HOME'] = './models'
    c_tts = coqui_tts({'model_name': 'tts_models/de/thorsten/tacotron2-DDC'})
    c_tts.tts("Hallo, Welt!")
