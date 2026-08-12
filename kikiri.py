#!/usr/bin/env python3
"""
Kokoro German: Test Inference
==============================
Tests the fine-tuned Kokoro model with a German phonetic test set.

Usage:
    # Zero-config sanity check (downloads reference model + voicepack from HF)
    python scripts/test_inference.py

    # Convert checkpoint + run inference
    python scripts/test_inference.py \
        --checkpoint StyleTTS2/logs/kokoro_german/epoch_1st_00002.pth \
        --voicepack voices/dm_daniel_epoch3.pt \
        --output-dir test_output/epoch3

    # Use a previously converted model
    python scripts/test_inference.py \
        --model voices/kokoro_german_epoch3.pth \
        --voicepack voices/dm_daniel_epoch3.pt

    # Run on CPU
    python scripts/test_inference.py \
        --checkpoint StyleTTS2/logs/kokoro_german/epoch_1st_00002.pth \
        --voicepack voices/dm_daniel_epoch3.pt \
        --device cpu
"""

import sys
from pathlib import Path
import torch
import numpy as np
from kokoro import KModel, KPipeline
import logging

logger: logging.Logger
logger = logging.getLogger(__file__)

# Prefer the kokoro submodule over any pip-installed kokoro package
#_repo_root = Path(__file__).resolve().parents[1]
#_kokoro_submodule = _repo_root / "kokoro"
#if _kokoro_submodule.exists() and str(_kokoro_submodule) not in sys.path:
#    sys.path.insert(0, str(_kokoro_submodule))

# Default reference model used for zero-config verification runs.
# When neither --checkpoint/--model nor --voicepack is provided, the script
# lazily downloads these from HuggingFace into a local cache directory so a
# fresh clone can run `uv run scripts/test_inference.py` with no arguments.

VOICES = {
    'martin': { 'repo': "kikiri-tts/kikiri-german-martin",
                'model_filename': "kikiri_german_martin_ep10.pth",
                'voice_filename': "voices/martin.pt" }
}
MODEL_CACHE_DIR = "models/.model_cache"
DEFAULT_DE_CONFIG = "kikiri-tts/training/config.json"

def download_reference_file(repo: str, filename: str,
                            cache_dir: str = MODEL_CACHE_DIR) -> Path:
    """Lazily download reference file from the default HF repo into a cache.

    Returns the local path. If file is already cached, no download occurs.
    """
    from huggingface_hub import hf_hub_download

    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    resolved = cache / filename
    if resolved.exists():
        print(f"Using cached reference file: {resolved}")
    else:
        print(f"Downloading reference file from {repo}: {filename}...")
        hf_hub_download(
            repo_id=repo,
            filename=filename,
            local_dir=str(cache),
        )
    return resolved


def auto_device(device: str = "auto"):
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device

def load_voice(model_path: Path, voicepack_path: Path,
                 config_path: str, device: str = "auto",):
    """Load the specified voice."""
    device = auto_device(device)

    # Load model with our fine-tuned weights and config
    logger.debug(f"Loading model {model_path} config: {config_path}")
    kmodel = KModel(repo_id="hexgrad/Kokoro-82M", config=config_path,
                         model=model_path.absolute())
    kmodel = kmodel.to(device).eval()

    # Create pipeline with German lang_code
    pipeline = KPipeline(lang_code="d", repo_id="hexgrad/Kokoro-82M",
                         model=kmodel)

    # Load voicepack
    logger.debug(f"Loading voicepack: {voicepack_path}")
    voice = torch.load(voicepack_path, map_location="cpu", weights_only=True)
    return kmodel, pipeline, voice

class kikiriki:
    def __init_de(self, voice_name: str, device: str = "auto",):
        voice_cfg = VOICES[voice_name]
        model_pth: str = voice_cfg["model_filename"]
        voicepack_pth: str = voice_cfg["voice_filename"]
        repo : str = voice_cfg["repo"]
        if (Path(MODEL_CACHE_DIR) / model_pth).exists():
            model_path = Path(MODEL_CACHE_DIR) / model_pth
        else:
            model_path = download_reference_file(repo, model_pth)

        # Resolve voicepack path: use explicit voicepack or fall back to the
        # default reference voicepack from HuggingFace.
        if (Path(MODEL_CACHE_DIR) / voicepack_pth).exists():
            voicepack_path = Path(MODEL_CACHE_DIR) / voicepack_pth
        else:
            voicepack_path = download_reference_file(repo, voicepack_pth)
        return load_voice(model_path, voicepack_path,
                          DEFAULT_DE_CONFIG, device=device)

    def __init__(self, lang_code="d", voice_name="", device="auto",):
        self.kmodel: KModel
        self.pipeline: KPipeline
        device = auto_device(device)
        logger.info(f"Initializing kokoro voice {voice_name}({lang_code}) on {device}")

        if lang_code and lang_code[0] == 'd':
            self.kmodel, self.pipeline, self.voice = \
              self.__init_de(voice_name, device)
            return
        # For all other languages, fall back to vanilla kokoro
        self.kmodel = KModel(repo_id='hexgrad/Kokoro-82M')
        self.pipeline = KPipeline(lang_code=lang_code,
                                  repo_id='hexgrad/Kokoro-82M',
                                  model=self.kmodel)
        voicepack_path = Path(MODEL_CACHE_DIR) / (voice_name + ".pt")
        if voicepack_path.exists():
            voice = torch.load(voicepack_path, map_location="cpu",
                               weights_only=True)
        else:
            voice = voice_name
        self.voice = self.pipeline.load_voice(voice)


    def tts(self, text):
        # Generate audio for sentence
        all_audio = []
        combined = np.array(np.float32)
        try:
            generator = self.pipeline(text, voice=self.voice, speed=1)
            for gs, ps, audio in generator:
                logger.debug(f"  phonemes: {ps[:60]}...")
                all_audio.append(audio)
                np.append(combined, np.array(audio))
            if all_audio:
                combined = np.concatenate(all_audio)
                duration_ms = len(combined) / 24.000
            else:
                logger.warn("No audio generated")
                return None, None
        except Exception as e:
            logger.error(f"Erro {e}")
            return None, None
        return (combined, duration_ms)
