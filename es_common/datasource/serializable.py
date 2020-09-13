import logging


class Serializable(object):
    def __init__(self):
        self.id = id(self)
        self.logger = logging.getLogger("Serializable")

    def serialize(self):
        raise NotImplemented()

    def deserialize(self, data, hashmap={}):
        raise NotImplemented()

    def get_property(self, data, name):
        try:
            p = data[name] if name in data.keys() else None
            return p
        except Exception as e:
            self.logger.error("Error while checking the property '{}' | {}".format(name, e))
            return None
