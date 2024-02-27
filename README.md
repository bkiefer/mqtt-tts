# Prerequisites for installation (tested on Ubuntu 22.04 [Mate])

```
sudo apt install python3-gst-1.0 libgirepository1.0-dev libcairo2-dev python3-pip espeak

conda create -n tts
conda activate tts
pip install -r requirements.txt
```

To download the TTS model, do

```
tts --text 'Dies ist ein Test' --model_name 'tts_models/de/thorsten/tacotron2-DDC'
```

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
