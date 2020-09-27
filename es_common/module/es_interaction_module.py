import logging

from es_common.datasource.serializable import Serializable
from es_common.model.interaction_block import InteractionBlock


class ESInteractionModule(Serializable):
    def __init__(self, origin_block, block_controller=None):
        super(ESInteractionModule, self).__init__()

        self.logger = logging.getLogger("ESInteractionModule")

        self.module_type = None
        self.block_controller = block_controller
        self.origin_block = origin_block
        self.next_int_block = None

        self.blocks_data = None
        self.execution_result = None

    def execute_module(self):
        success = self.start_module()
        self.logger.info("Module execution was{}successful".format(" " if success else " not "))

        if success is False:
            return self.origin_block

        self.load_blocks_data()
        next_block = self.get_starting_block()
        return next_block

    def start_module(self):
        # To be implemented in child classes
        return True

    def load_blocks_data(self):
        try:
            # self.blocks_data = data_helper.load_data_from_file(self.design_file)
            self.blocks_data = self.origin_block.design_module.get_file_data()
        except Exception as e:
            self.logger.error("Error while loading hidden blocks! {}".format(e))

    def get_next_interaction_block(self, current_interaction_block, execution_result=None):
        self.execution_result = execution_result
        try:
            self.logger.info("Searching for next interaction block...")
            if current_interaction_block is None or self.blocks_data is None:
                return None

            output_socket_id = self.get_socket_id(current_interaction_block.id, socket_lst_name="outputs")
            input_sockets_id_lst = []
            # get the list of attached edges
            for edge in self.blocks_data["edges"]:
                if output_socket_id == edge["start_socket"]:
                    input_sockets_id_lst.append(edge["end_socket"])
                elif output_socket_id == edge["end_socket"]:
                    input_sockets_id_lst.append(edge["start_socket"])

            self.logger.info("Socket {} is connected to {} {}".format(output_socket_id,
                                                                      len(input_sockets_id_lst), input_sockets_id_lst))

            next_block_dict = None
            next_int_block = None
            if len(input_sockets_id_lst) > 0:
                if execution_result is None or execution_result == "":
                    # get output socket id
                    next_block_dict = self._get_interaction_block_by_socket_id(input_sockets_id_lst[0],
                                                                               socket_lst="inputs")
                    # self.logger.info("Next block dict: {}".format(next_block_dict))
                else:
                    # check the answers
                    for i in range(len(current_interaction_block.topic_tag.answers)):
                        # if the result is in the answers ==> go to appropriate interaction block
                        if execution_result.lower() in current_interaction_block.topic_tag.answers[i].lower():
                            goto_id = current_interaction_block.goto_ids[i]
                            next_block_dict = self._get_interaction_block_dict_by_id(goto_id)

            if next_block_dict:
                next_int_block = InteractionBlock.create_interaction_block(next_block_dict)
                self.logger.info("Next int block: {}".format(next_int_block.to_dict))
                if next_int_block:
                    next_int_block.id = next_block_dict["id"]
                    next_int_block.is_hidden = True
                    next_int_block.execution_result = execution_result

            self.next_int_block = next_int_block
            self.update_next_block_fields()
            self.logger.info("Found another block: {}".format(self.next_int_block.message))
        except Exception as e:
            self.logger.error("Error while getting the next block: {}".format(e))
        finally:
            return self.next_int_block

    def update_next_block_fields(self):
        # To be implemented in child classes
        pass

    def get_starting_block(self):
        int_block = None
        if self.blocks_data:
            for block in self.blocks_data["blocks"]:
                try:
                    int_block_dict = block["parent"]
                    if int_block_dict["pattern"].lower() == "start":
                        int_block = InteractionBlock.create_interaction_block(int_block_dict)
                        if int_block:
                            int_block.id = int_block_dict["id"]
                            int_block.is_hidden = True
                        break
                except Exception as e:
                    self.logger.error("Error while creating a block. {}".format(e))
                    continue
            # check if the scene contains a valid start block
            # block = self.block_controller.get_hidden_block(pattern="start")
            self.logger.info("The loaded data {} a starting block.".format(
                "doesn't contain" if int_block is None else "contains"))

        return int_block

    def get_socket_id(self, int_block_id, socket_lst_name="outputs"):
        if self.blocks_data:
            for block in self.blocks_data["blocks"]:
                if block["parent"]["id"] == int_block_id:
                    return block[socket_lst_name][0]["id"] if len(block[socket_lst_name]) > 0 else None

        return None

    def _get_interaction_block_by_socket_id(self, socket_id, socket_lst="outputs"):
        if self.blocks_data and socket_id:
            for block in self.blocks_data["blocks"]:
                sockets = block[socket_lst]
                if len(sockets) > 0 and sockets[0]["id"] == socket_id:
                    self.logger.info("Found a parent block.")
                    return block["parent"]

        return None

    def _get_interaction_block_dict_by_id(self, id_val):
        if self.blocks_data and id_val:
            for block in self.blocks_data["blocks"]:
                if block["parent"]["id"] == id_val:
                    return block["parent"]
        return None

    def serialize(self):
        raise NotImplementedError

    def deserialize(self, data, hashmap={}):
        raise NotImplementedError
