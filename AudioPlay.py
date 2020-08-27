########################################################################
#audio setup
########################################################################
import json
import os.path
from os import path
import pygame

import threading
from MqttClient import MQTTClient

Mqtt = MQTTClient()
Mqtt.MqttPathPublish = "your path to publish"
Mqtt.MqttPathSubcribe = "AudioPlay"


class myThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
    def run(self):
        Mqtt.mqttSubcribe()

queueLock = threading.Lock()
thread = myThread(1, "thread1")
thread.start()

########################################################################
#audio setup
def playAudio(_filename):
    pygame.mixer.init()
    pygame.mixer.music.load("/home/pi/maychamcong/audio/" + _filename)
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        pass

########################################################################

print "start AudioPlay!"
while True:
    _waitData = Mqtt.getData()
    if _waitData != None:
	print _waitData
        waitData = json.loads(_waitData)
        playAudio(waitData["data"] + ".mp3")
