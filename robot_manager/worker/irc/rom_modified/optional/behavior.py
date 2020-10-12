from twisted.internet.defer import inlineCallbacks, returnValue

from naoqi import ALProxy

from rom_naoqi.rom.actuator.actuator_modality import ActuatorModality

class Behavior(ActuatorModality):

    name = u'rom.optional.behavior.'

    infomap = {
        'play': [],
        'stop': u'Stop the current behavior from running',
        'wakeup': u'Wakes the robot up and sets the Motors on',
        'rest': u'Rests the robot and sets the Motors off'
    }

    def __init__(self):
        ActuatorModality.__init__(self)
        self.behavior_manager = ALProxy('ALBehaviorManager')
        self.posture_manager = ALProxy('ALRobotPosture')
        self.motion = ALProxy('ALMotion')
        self.hands = [
            'BlocklyLeftHandClosed',
            'BlocklyRightHandClosed',
            'BlocklyLeftHandOpen',
            'BlocklyRightHandOpen']
        self.infomap['play'] = [u'' + behavior[behavior.find("/")+1:]
            for behavior in self.behavior_manager.getInstalledBehaviors()]

    def register(self, sess):
        ActuatorModality.register(self, sess)
        # Register write
        sess.register(self.play, self.name + 'play')
        sess.register(self.wakeup, self.name + 'wakeup')
        sess.register(self.rest, self.name + 'rest')

    @inlineCallbacks
    def play(self, name='', sync=True):
        if name in Behavior.infomap['play']: # Only play predifined behaviors in infomap
            frame = {'data': {'body': name}, 'time': 0}
            yield ActuatorModality.write(self, [frame], 'none', sync)
        returnValue(None)

    def write_frame(self, frame, _):
        behavior = str(frame['data']['body'])

        if behavior not in self.hands:
            self.motion.setAngles(['LHand','RHand'],[0.2,0.2],0.2)
        try:
            if behavior.startswith('Stand/') and \
               not self.posture_manager.getPosture().startswith('Stand'):
                print 'Incompatible start posture: ' + behavior
                return
            self.behavior_manager.runBehavior(behavior)
        except RuntimeError:
            print 'Behavior not found: ' + behavior

    def stop(self):
        ActuatorModality.stop(self)
        self.behavior_manager.stopAllBehaviors()

    def validate(self, frames, force):
        # Disable validation.
        pass

    def populate(self, frames, mode):
        # Disable population.
        pass

    def wakeup(self):
        self.motion.wakeUp()

    def rest(self):
        self.motion.rest()
