import logging

from es_common.datasource.serializable import Serializable


class ESCommand(Serializable):
    def __init__(self, is_speech_related=False):
        super(ESCommand, self).__init__()

        self.is_speech_related = is_speech_related
        self.command_type = None

    def clone(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def serialize(self):
        raise NotImplementedError

    def deserialize(self, data, hashmap={}):
        raise NotImplementedError
