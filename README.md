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

# Creating a docker file instead (recommended)

Make sure you have properly installed docker and your user is member of the `docker` group. Now execute

    ./build_docker.sh

To start the TTS server, execute `./run_docker.sh my_docker_config.sh`. Adapt the config files to your needs, and don't forget to download the necessary models beforehand.

# Available TTS implementations

Currently, this module offers you two options: coqui TTS and Kikiri TTS (kokoro including a german voice). The first forbids commercial applications, which is why the second alternative was added.

## Kokoro / Kikiri models

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

## Coqui

To download the TTS model for coqui, you first have to create the docker image. Select your model based on the `coqui_models.txt` file and execute for example

    ./coqui_dld_model.sh 'tts_models/de/thorsten/tacotron2-DDC'

This will place the necessary files into the `models` subdirectory, possibly into hidden subdirectories

# Running the server

Start your favorite MQTT broker first. Then either start the docker container or locally:

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
