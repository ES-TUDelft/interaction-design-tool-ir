import time

from naoqi import ALProxy

from rom_naoqi.rom.frame import Frame
from rom_naoqi.rom.sensor.event_modality import EventModality


class TabletInput(EventModality):
    name = u'rom.optional.tablet_input.'

    infomap = {
        'ubi': {
            'body': u'returns a string',
        },
        'default': EventModality.default_ubi[0]
    }

    def __init__(self):
        EventModality.__init__(self)
        self.memory = ALProxy('ALMemory')
        self.subscribed = False

    def register(self, sess):
        EventModality.register(self, sess)

    def on_tablet_input(self, _, value):
        """
        NAOqi event callback.
        """
        frame = Frame(time.time() * 1000)
        frame.raw['body'] = {
            u'text': u'' + value
        }
        self.tick(frame)

    def remap(self):
        if self.filter and not self.subscribed:
            self.memory.subscribeToEvent('TabletInput', self.getName(), 'on_tablet_input')
            self.subscribed = True
        if self.subscribed and not self.filter:
            self.memory.unsubscribeToEvent('TabletInput', self.getName())
            self.subscribed = False

    def __del__(self):
        if self.subscribed:
            self.memory.unsubscribeToEvent('TabletInput', self.getName())
