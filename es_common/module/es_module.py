import logging

from block_manager.factory.block_factory import BlockFactory
from es_common.utils import data_helper

INT_DESIGN_FILE = "es_common/module/interaction_design/reservations.json"


class ESModule(object):
    def __init__(self, block_controller, origin_block=None):
        self.logger = logging.getLogger("ESModule")

        self.module_type = None
        self.design_file = INT_DESIGN_FILE
        self.block_controller = block_controller
        self.origin_block = origin_block

        self.block_controller.hidden_scene = BlockFactory.create_scene()
        self.blocks_data = None

    def start_module(self):
        # TODO
        self.logger.info("Started executing")
        return False

    def get_next_block(self):
        success = self.start_module()

        if success is True:
            next_block = self.get_starting_block()
            return next_block
        else:
            return self.origin_block

    def get_blocks_data(self):
        self.blocks_data = data_helper.load_data_from_file(self.design_file)
        if self.blocks_data:
            self.block_controller.hidden_scene.load_scene_data(self.blocks_data)
            # mark them as hidden
            for block in self.block_controller.get_hidden_blocks():
                if block and block.parent:
                    block.parent.is_hidden = True
            self.logger.info("Successfully loaded data into hidden scene.")

    def get_starting_block(self):
        # check if the scene contains a valid start block
        block = self.block_controller.has_hidden_block(pattern="start")
        self.logger.info("The hidden scene {} a starting block.".format(
            "doesn't contain" if block is None else "contains"))

        return block
