# Prerequisites for installation (tested on Ubuntu 22.04 [Mate])

```
sudo apt install python3-gst-1.0 libgirepository1.0-dev libcairo2-dev python3-pip espeak

conda create -n tts
conda activate tts
pip install -r requirements.txt
```

# Running the server

Start your favorite MQTT broker first. Then:

    python3 tts-server.py

Send this message to `tts/behaviour`, e.g., with MQTT-Explorer

    { "id": 222, "text": "Das ist ein wirklich total unsinniger text" }

# Training a new model

docker run -ti --rm --gpus all --shm-size=32g --entrypoint /bin/bash -v `pwd`:/local/ ghcr.io/coqui-ai/tts
# im docker
cd /local/speedy_speech
CUDA_VISIBLE_DEVICES="0, 1, 2, 3" python3 -m trainer.distribute --script train_speedy_speech.py
