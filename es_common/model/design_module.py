import logging
import os

import random

from es_common.utils import data_helper


class DesignModule(object):
    def __init__(self, name="", filename="", folder_name="", randomize=False):
        self.logger = logging.getLogger("DesignModule")

        self.name = name
        self._folder_name = self.folder_name = folder_name
        self.randomize = randomize

        self.available_files = []
        self.selected_files = []

        self.filename = filename

    def get_file_data(self):
        try:
            data = data_helper.load_data_from_file(self.filename)
            # "{}{}".format(os.path.expanduser('~'), self.filename))
            return data, self._filename
        except Exception as e:
            self.logger.error("Error while while loading data from {} | {}".format(self._filename, e))
            return None, None

    @property
    def filename(self):
        if self.randomize is False:
            return self._filename

        try:
            if len(self.selected_files) == 0:  # start
                self.available_files = os.listdir(self.folder_name)
                for f in self.available_files:
                    if ".json" not in f:
                        self.available_files.remove(f)
            elif len(self.available_files) == 0:  # restart
                self.available_files = self.selected_files
                self.selected_files = []
            # select a random file
            filename = self.available_files[random.randint(0, len(self.available_files)-1)]
            self.available_files.remove(filename)
            self.selected_files.append(filename)
            # set the filename
            self.filename = "{}/{}".format(self.folder_name, filename)

            return self._filename
        except Exception as e:
            self.logger.error("Error while setting module filename: {}".format(e))

    @filename.setter
    def filename(self, filename):
        self._filename = DesignModule.remove_cwd(filename)

    @property
    def folder_name(self):
        return self._folder_name

    @folder_name.setter
    def folder_name(self, folder_name):
        self._folder_name = DesignModule.remove_cwd(folder_name)

    def clone(self):
        return DesignModule(self.name, self._filename, self.folder_name, self.randomize)

    # ============== #
    # HELPER METHODS #
    # ============== #
    @property
    def to_dict(self):
        return {
            'name': self.name,
            'filename': self._filename,
            'folder_name': self.folder_name,
            'randomize': self.randomize
        }

    @staticmethod
    def create_design_module(module_dict):
        try:
            if module_dict:
                return DesignModule(module_dict["name"], module_dict["filename"],
                                    module_dict["folder_name"], module_dict["randomize"])
            return None
        except Exception as e:
            print("Error while creating module from {} | {}".format(module_dict, e))
            return None

    @staticmethod
    def remove_cwd(txt):
        # if os.path.expanduser('~') in txt:
        #     txt = txt.replace(os.path.expanduser('~'), "")
        cwd = "{}/".format(os.getcwd())
        if cwd in txt:
            return txt.replace(cwd, "")
        return txt
