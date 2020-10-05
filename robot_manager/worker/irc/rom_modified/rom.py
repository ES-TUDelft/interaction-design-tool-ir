import os
import time

from twisted.internet import reactor, threads
from twisted.internet.defer import inlineCallbacks, returnValue
from autobahn.twisted.util import sleep

from rom_naoqi.rom.data import Data
# Actuator modalities
from rom_naoqi.rom.actuator.motor import Motor
from rom_naoqi.rom.actuator.light import Light
from rom_naoqi.rom.actuator.audio import Audio
# Sensor modalities
from rom_naoqi.rom.sensor.sight import Sight
from rom_naoqi.rom.sensor.hearing import Hearing
from rom_naoqi.rom.sensor.touch import Touch
from rom_naoqi.rom.sensor.proprio import Proprio
# Optional modalities
from rom_naoqi.rom.optional.behavior import Behavior
from rom_naoqi.rom.optional.posture import Posture
from rom_naoqi.rom.optional.tts import Tts
from rom_naoqi.rom.optional.card_detection import CardDetection
from rom_naoqi.rom.optional.face_detection import FaceDetection
from rom_naoqi.rom.optional.keyword import Keyword
from rom_naoqi.rom.optional.tablet import Tablet
from rom_naoqi.rom.optional.tablet_input import TabletInput

class Rom(object):

    def __init__(self):
        # The desired amount of frames per second
        # Might not be reached if load is high
        self.fps = 16
        self.running = False
        self.timestamp = 0
        self.clean_timestamp = 0
        self.data = Data()
        self.is_nao = self.data.robot()['model'] == 'nao'
        # Actuator modalities
        self.motor = Motor()
        self.light = Light()
        self.audio = Audio()
        # Sensor modalities
        self.sight = Sight()
        self.hearing = Hearing()
        self.proprio = Proprio()
        self.touch = Touch()
        # Optional modality
        self.behavior = Behavior()
        self.posture = Posture()
        self.tts = Tts()
        self.face = FaceDetection(self.fps)
        self.card = CardDetection()
        self.keyword = Keyword()
        if not self.is_nao:
            self.tablet = Tablet()
            self.tablet_input = TabletInput()
        # Add Actuator modalities to Data model
        self.data.infomap['actuator'] = {
            'motor': self.motor.info(),
            'light': self.light.info(),
            'audio': self.audio.info()
        }
        # Add Sensor modalities to Data model
        self.data.infomap['sensor'] = {
            'sight': self.sight.info(),
            'hearing': self.hearing.info(),
            'proprio': self.proprio.info(),
            'touch': self.touch.info()
        }
        # Add Optional modalities to Data model
        self.data.infomap['optional'] = {
            'behavior': self.behavior.info(),
            'posture': self.posture.info(),
            'tts': self.tts.info(),
            'face': self.face.info(),
            'card': self.card.info(),
            'keyword': self.keyword.info()
        }
        if not self.is_nao:
            self.data.infomap['optional']['tablet'] = self.tablet.info()
            self.data.infomap['optional']['tablet_input'] = self.tablet_input.info()

    def register(self, sess):
        self.sess = sess
        self.data.register(sess)
        # Actuator modalities
        self.motor.register(sess)
        self.light.register(sess)
        self.audio.register(sess)
        # Sensor modalities
        self.sight.register(sess)
        self.hearing.register(sess)
        self.proprio.register(sess)
        self.touch.register(sess)
        # Optional modality
        self.behavior.register(sess)
        self.posture.register(sess)
        self.tts.register(sess)
        self.card.register(sess)
        self.face.register(sess)
        self.keyword.register(sess)
        self.tablet_input.register(sess)
        if not self.is_nao:
            self.tablet.register(sess)

    @inlineCallbacks
    def run(self):
        """
        Run starts the main loop that handles all output from the robot
        and streams the required sensor data
        """
        if self.running:
            return
        self.running = True
        print 'Starting pinger'
        reactor.callLater(10, self.ping)
        print 'Running the main loop'
        self.clean_timestamp = 0
        while self.running:
            self.timestamp = time.time()*1000
            yield self.tick()
            self.clean()
            yield self.sync_sleep()
        print 'The main loop is terminated'
        returnValue(None)

    @inlineCallbacks
    def tick(self):
        # Sensor modalities
        s = threads.deferToThread(self.sight.tick, self.timestamp)
        h = threads.deferToThread(self.hearing.tick, self.timestamp)
        self.touch.tick(self.timestamp)
        self.proprio.tick(self.timestamp)
        # Optional modality
        self.face.tick(self.timestamp)
        # Yields
        yield s
        yield h

    def clean(self):
        if self.timestamp-self.clean_timestamp > 10*1000:
            # Sensor modalities
            self.sight.clean()
            self.hearing.clean()
            self.touch.clean()
            self.proprio.clean()
            # Optional modality
            self.face.clean()
            self.card.clean()
            self.keyword.clean()
            self.tablet_input.clean()
            self.clean_timestamp = self.timestamp

    @inlineCallbacks
    def sync_sleep(self):
        yield sleep((0-time.time()) % (1.0/self.fps))

    def kill(self):
        """
        Stop the main loop
        """
        self.running = False
        ## TODO: clean streams and readers from modalities

    @inlineCallbacks
    def ping(self):
        call = self.sess.call(u'rie.robotmanager.ping')
        try:
            yield call.addTimeout(10, reactor)
            reactor.callLater(10, self.ping)
        except:
            yield self.tts.say('ik ben mijn verbinding kwijt')
            os._exit(1)
