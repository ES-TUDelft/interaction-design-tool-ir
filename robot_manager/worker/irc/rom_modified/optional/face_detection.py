from naoqi import ALProxy

from rom_naoqi.rom.sensor.sensor_modality import SensorModality

class FaceDetection(SensorModality):

    name = u'rom.optional.face.'

    infomap = {
        'ubi': {
            'body': u'list of faces with [abs-x, abs-y, size, rel-x rel-y] in rads for each face',
        },
        'default': u'body'
    }

    def __init__(self, fps):
        SensorModality.__init__(self)
        self.fps = fps
        self.face_detection = ALProxy('ALFaceDetection')
        self.memory = ALProxy('ALMemory')
        self.tracker = ALProxy('ALTracker')
        self.face_size = 0.1
        self.subscribed = False

    def register(self, sess):
        SensorModality.register(self, sess)
        # register tracker
        sess.register(self.face_tracker, self.name + 'face_tracker')

    def poll(self, frame):
        if not self.filter:
            return
        data = self.memory.getData('FaceDetected', 0)
        faces = []
        if data:
            faces = data[1]
            #removing the recog info
            faces.pop()
            # Get head rotation
            hx = self.memory.getData('Device/SubDeviceList/HeadYaw/Position/Sensor/Value')
            hy = self.memory.getData('Device/SubDeviceList/HeadPitch/Position/Sensor/Value')
        res = [
            [
                hx+f[0][1],# absolute face x angle
                hy+f[0][2],# absolute face y angle
                max(f[0][3],f[0][4]),# face size
                f[0][1],# relative face x angle
                f[0][2]# relative face y angle
            ] for f in faces]#list of faces
        frame.raw['body'] = res

    def diff(self, frame, ubi):
        if self.sensitivity < 0:
            return True
        return frame.raw[ubi] != self.state.raw[ubi]

    def remap(self):
        if self.filter and not self.subscribed:
            self.face_detection.subscribe(self.getName(), 1000/self.fps, 0.0)
            self.subscribed = True
        if self.subscribed and not self.filter:
            self.face_detection.unsubscribe(self.getName())
            self.subscribed = False

    def __del__(self):
        self.face_detection.unsubscribe(self.getName())

    def face_tracker(self, start=False):
        target_name = "Face"
        if start is True:
            self.tracker.registerTarget(target_name, self.face_size)
            self.tracker.track(target_name)
        else:
            self.tracker.stopTracker()
            self.tracker.unregisterAllTargets()
