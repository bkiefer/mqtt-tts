# Prerequisites for installation (tested on Ubuntu up to 26.04 [Mate])

These installation instructions are tested on Ubuntu 22.04, up to 26.04, and use the `uv` package management system to provide the required python packages. If you don't have it installed yet, check here: [install uv](https://docs.astral.sh/uv/getting-started/installation/).

Install python bindings for the gstreamer libraries and `espeak`:

```
# up to Ubuntu 25.10
sudo apt install python3-gst-1.0 libgirepository1.0-dev libcairo2-dev espeak
# 26.04
sudo apt install python3-gst-1.0 libgirepository2.0-dev libcairo2-dev espeak
```

After the installation, libcairo-dev and its dependencies *can* be removed:

```
sudo apt remove libcairo2-dev
sudo apt autoremove
```

Currently, this module offers you two options: coqui TTS and Kikiri TTS (kokoro including a german voice). The first forbids commercial applications, which is why the second alternative was added.


To download one of the non-German kokoro voices (e.g. if_sara (italian, female))

    wget https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/if_sara.pt

and put it into `models/.model_cache`. Check the huggingface page for available voices.

For the German voices:
- Female voice (victoria)

```
    wget https://huggingface.co/kikiri-tts/kikiri-german-victoria/resolve/main/kikiri_german_victoria_ep10.pth
    wget https://huggingface.co/kikiri-tts/kikiri-german-victoria/resolve/main/voices/victoria.pt
```
- Male voice (martin)

```
    wget https://huggingface.co/kikiri-tts/kikiri-german-martin/resolve/main/kikiri_german_martin_ep10.pth
    wget https://huggingface.co/kikiri-tts/kikiri-german-martin/resolve/main/voices/martin.pt
```
put the `.pth` files into the `models/.model_cache` folder and the `.pt` files into `models/.model_cache/voices`

then put it into the models/.model_cache directory.

To download the TTS model for coqui, do (Does not work, find another way)

    tts --text 'Dies ist ein Test' --model_name 'tts_models/de/thorsten/tacotron2-DDC'

This will generate a wav file that can be played to check if it works.

# Running the server

Start your favorite MQTT broker first. Then:

    python3 tts-server.py

Send this message to `tts/behaviour`, e.g., with MQTT-Explorer

    { "id": 222, "text": "Das ist ein wirklich total unsinniger text" }

The server currently uses the default pulseaudio sink. To set this to the ReSpeaker device, you execute the following on the command line:

```
pacmd set-default-sink 'alsa_output.usb-SEEED_ReSpeaker_4_Mic_Array__UAC1.0_-00.analog-stereo'
```

To check, if ReSpeaker is the default, use this;

```
pacmd list-sinks | grep -e 'index:' -e device.string -e 'name:'
```



# Training a new model

docker run -ti --rm --gpus all --shm-size=32g --entrypoint /bin/bash -v `pwd`:/local/ ghcr.io/coqui-ai/tts
# im docker
cd /local/speedy_speech
CUDA_VISIBLE_DEVICES="0, 1, 2, 3" python3 -m trainer.distribute --script train_speedy_speech.py
