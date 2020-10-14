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
        # and interval for video frames
        self.fps = 12
        self.rate = 1
        # Total ticks and ticks at last clean
        # In that case the desired fps is not reached
        # the rom increases the interval for video frames
        # based on the true fps, but tries to keep it above 1 fps
        self.ticks = 0
        self.cticks = 0
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
        self.sight = Sight(self.fps)
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

        self._init_tablet_input()

    def _init_tablet_input(self):
        if not self.is_nao:
            self.data.infomap['optional']['tablet_input'] = self.tablet_input.info()
            self.tablet_input = TabletInput()

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
        if not self.is_nao:
            self.tablet.register(sess)
            self.tablet_input.register(sess)

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
            self.tick()
            self.clean()
            self.ticks += 1
            yield self.sync_sleep()
        print 'The main loop is terminated'
        returnValue(None)

    def tick(self):
        # Sensor modalities
        if not (self.ticks % self.rate):
            self.sight.tick(self.timestamp)
        self.hearing.tick(self.timestamp)
        self.touch.tick(self.timestamp)
        self.proprio.tick(self.timestamp)
        # Optional modality
        self.face.tick(self.timestamp)

    def clean(self):
        t = self.timestamp-self.clean_timestamp
        if t > 10*1000:
            # Calculate true fps
            f = self.ticks - self.cticks
            self.cticks = self.ticks
            tfps = f/(t/1000)
            # If true fps is to low, increase the video frame interval
            if tfps and tfps < self.fps:
                self.rate = min(round(self.rate*self.fps / tfps),self.fps)
            # Sensor modalities
            self.sight.clean()
            self.hearing.clean()
            self.touch.clean()
            self.proprio.clean()
            # Optional modality
            self.face.clean()
            self.card.clean()
            self.keyword.clean()
            self.clean_timestamp = self.timestamp
            if self.tablet_input:
                self.tablet_input.clean()

    @inlineCallbacks
    def sync_sleep(self):
        sleep_time = (0-time.time()) % (1.0/self.fps)
        # We sleep a minimum of 10ms
        # this allows the network to send stuff
        yield sleep(max(sleep_time, 0.01))

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
