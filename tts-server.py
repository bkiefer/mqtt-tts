#!/usr/bin/env python
from TTS.api import TTS
from gst_tts_source import GStreamerSource
import json
from threading import Thread
from queue import Queue
import sys
import yaml
import logging

logger: logging.Logger
logger = logging.getLogger(__file__)

from mqtt_client import MqttClient

# Get device
# device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cpu"

class MqttTTSServer(MqttClient):
  def _on_control_msg(self, client, userdata, message):
    message = message.payload.decode()
    logger.info(f'control message: {message}')
    match message:
      case 'exit':
        self.stop()

  def _on_behaviour_message(self, client, userdata, message):
    # print("Received message '" + str(message.payload) + "' on topic '"
    #    + message.topic + "' with QoS " + str(message.qos))
    behaviour = json.loads(message.payload)
    self.queue.put(behaviour)

  def __init__(self, config):
    super().__init__('tts', config.get('mqtt') or {})
    self.is_running = True
    self.queue = Queue()
    self.config = config
    in_topic = config.get('in_topic') or self.with_pid("behaviour")
    self.topics[in_topic] = self._on_behaviour_message
    self.topics[self.with_pid('control')] = self._on_control_msg
    self.out_topic = config.get('out_topic') or "dialogue/messages"
    self.model_name = config['model_name'] if 'model_name' in config \
      else "tts_models/de/thorsten/tacotron2-DDC"
    self.tts = TTS(model_name=self.model_name, progress_bar=False).to(device)

  def _tts(self, text: str, id: str):
    # Run TTS
    self.tts_start(id)
    if not text:
      print("WARNING: no TEXT for TTS!")
    else:
      wav = self.tts.tts(text=text)
      duration_ms = 0.1 + len(wav)/22.050
      GStreamerSource().send_chunk(wav, duration_ms=int(duration_ms))
    self.tts_end(id)

  def tts_start(self, id):
    msg = '{ "status": "tts_started", "id": "' + str(id) + '" }'
    msginfo = self.client.publish(self.out_topic, msg)
    msginfo.wait_for_publish()

  def tts_end(self, id):
    msg = '{ "status": "tts_stopped", "id": "' + str(id) + '" }'
    self.client.publish(self.out_topic, msg)

  def watch_queue(self):
    while self.is_running:
      behaviour = self.queue.get(block=True)
      if (behaviour is not None):
        try:
          self._tts(behaviour["text"], behaviour["id"])
        except KeyError as ex:
          print("Error {}: {}".format(type(ex), ex))

  def stop(self):
    if self.is_running:
      self.is_running = False
      self.queue.put(None)

  def run(self):
    try:
      self.mqtt_connect()
      self.watch_queue()
    except Exception as e:
      print('Error in initialization: {}'.format(e))
      self.stop()
    finally:
      print('Disconnecting...')
      self.mqtt_disconnect()


if __name__ == '__main__':
  #logging.basicConfig(filename='example.log', encoding='utf-8', level='DEBUG',
  #                    format=('%(levelname)s %(funcName)s:%(lineno)s %(message)s'),)
  config = {}
  if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
      config = yaml.safe_load(f)

  MqttTTSServer(config).run()
