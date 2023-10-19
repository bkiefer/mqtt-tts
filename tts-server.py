import torch
from TTS.api import TTS
from gst_tts_source import GStreamerSource
import json
import paho.mqtt.client as mqtt
from threading import Thread
from queue import Queue

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"
device = "cpu"

class MqttTTSServer():
  # Init TTS with the target model name
  tts = None
  in_topic = "tts/behaviour"
  out_topic = "dialogue/messages"
  model_name = "tts_models/de/thorsten/tacotron2-DDC"
  msg_queue = Queue()
  play_thread: Thread = None

  def __init__(self, config):
    self.config = config
    if 'in_topic' in config:
      self.in_topic = config['in_topic']
    if 'channels' in config:
      self.out_topic = config['out_topic']
    if 'model_name' in config:
      self.model_name = config['model_name']
    self.tts = TTS(model_name=self.model_name, progress_bar=False).to(device)
    self.__init_mqtt_client()

  def __init_mqtt_client(self):
    self.client = mqtt.Client()
    # self.client.username_pw_set(self.mqtt_username, self.mqtt_password)
    self.client.on_message = self._on_message
    self.client.on_connect = self._on_connect
    self.client.on_subscribe = self._on_subscribe

  def mqtt_connect(self):
    host = 'localhost'
    if 'mqtt_address' in self.config:
      host = self.config['mqtt_address']
    print("connecting to: " + host + " ", end="")
    self.client.connect(host)
    self.client.subscribe(self.in_topic)
    self.client.loop_forever()

  def mqtt_disconnect(self):
    self.client.loop_stop()
    self.client.disconnect()

  def _on_connect(self, client, userdata, flags, rc):
    print('CONNACK received with code %d. ' % (rc), end="")

  def _on_subscribe(self, client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

  def _on_message(self, client, userdata, message):
    #print("Received message '" + str(message.payload) + "' on topic '"
    #    + message.topic + "' with QoS " + str(message.qos))
    behaviour = json.loads(message.payload)
    self.msg_queue.put(behaviour)

  def _tts(self, text: str, id: str):
    # Run TTS
    self.tts_start(id)
    wav = self.tts.tts(text=text)
    duration_ms = 0.1 + len(wav)/22.050
    GStreamerSource().send_chunk(wav, duration_ms=duration_ms)
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
      behaviour = self.msg_queue.get(block=True)
      if (behaviour is not None):
        self._tts(behaviour["text"], behaviour["id"])

  def run(self):
    try:
      self.is_running = True
      self.play_thread = Thread(target=self.watch_queue, daemon=True)
      self.play_thread.start()
      self.mqtt_connect()
    except Exception as e:
      print('Error in initialization: {}'.format(e))
    finally:
      print('Disconnecting...')
      self.is_running = False
      self.msg_queue.put(None)
      self.mqtt_disconnect()

if __name__ == '__main__':
  #logging.basicConfig(filename='example.log', encoding='utf-8', level='DEBUG',
  #                    format=('%(levelname)s %(funcName)s:%(lineno)s %(message)s'),)
  config = { }
  MqttTTSServer(config).run()
