#!/usr/bin/env python
from gst_tts_source import GStreamerSource
import json
from queue import Queue
import sys
import yaml
import logging
import time

logger: logging.Logger
logger = logging.getLogger(__file__)

from mqtt_client import MqttClient
from coqui import coqui_tts
from kikiri import kikiriki

# Get device
# device = "cuda" if torch.cuda.is_available() else "cpu"
def time_string(secs: float):
    """Return a time string 'hours:minutes:seconds.msecs'."""
    mins = int(secs / 60)
    hours = int(mins / 60)
    secs = secs - mins * 60
    mins = mins - hours * 60
    return f"{hours:02d}:{mins:02d}:{secs:06.3f}"

def time_it(print_func=print):
  def inner_deco(func):
    """Decorate some function to measure wall time."""

    def timed_func(*args, **kwargs):
      start = time.time()
      result = func(*args, **kwargs)
      end = time.time()
      print_func(f"Elapsed time: {time_string(end - start)}")
      return result

    return timed_func

  return inner_deco

class MqttTTSServer(MqttClient):
  def _on_control_msg(self, client, userdata, message):
    message = message.payload.decode()
    match message:
      case 'exit':
        self.stop()

  def _on_behaviour_message(self, client, userdata, message):
    try:
      behaviour = json.loads(message.payload)
    except ValueError as ex:
      logger.error("Could not parse JSON: {}".format(ex))
      return
    self.queue.put(behaviour)

  def with_pid(self, suffix: str):
    return self.pid + '/' + suffix

  def __init__(self, config):
    super().__init__('tts', config.get('mqtt', {}))
    self.is_running = False
    self.queue = Queue()
    self.config = config
    in_topic = config.get('in_topic') or self.with_pid("behaviour")
    self.topics[in_topic] = self._on_behaviour_message
    self.topics[self.with_pid('control')] = self._on_control_msg
    self.out_topic = config.get('out_topic') or "dialogue/messages"
    if 'kikiri' in config:
      conf = config['kikiri']
      lang = conf.get("lang_code","d")
      voice = conf.get("voice_name", "martin")
      device = conf.get("device", "cpu")
      self.tts_module = kikiriki(lang, voice, device)
    elif "coqui" in config:
      conf = config['coqui']

      self.tts_module = coqui_tts(config['coqui'])
    else:
      logger.error("No usable TTS section found (either kikiri or coqui)")
      sys.exit(1)
    logger.info("TTS initialized")

  @time_it(logger.debug)
  def _timed_tts(self, text):
    return self.tts_module.tts(text)

  def _tts(self, text: str, id: str):
    # Run TTS
    self.tts_start(id)
    if not text:
      logger.warning("No TEXT for TTS")
    else:
      audio, duration_ms = self._timed_tts(text)
      if audio is not None:
        GStreamerSource(pipeline = config.get('pipeline', None)) \
            .send_chunk(audio, duration_ms=int(duration_ms))
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
          logger.error("{}: {}".format(type(ex), ex))

  def stop(self):
    if self.is_running:
      self.is_running = False
      self.queue.put(None)

  def run(self, wait_forever=False):
    try:
      self.is_running = True
      self.mqtt_connect(forever=wait_forever)
      self.watch_queue()
    except Exception as e:
      logger.error('Error in initialization: {}'.format(e))
      self.stop()
    finally:
      self.mqtt_disconnect()


if __name__ == '__main__':
  logging.basicConfig(encoding='utf-8', level='INFO',
                      format=('%(levelname)s %(message)s'),
                      stream=sys.stderr)
  #logging.basicConfig(filename='example.log', encoding='utf-8', level='DEBUG',
  #                    format=('%(levelname)s %(funcName)s:%(lineno)s %(message)s'),)
  config = {}
  if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
      config = yaml.safe_load(f)

  MqttTTSServer(config).run()
