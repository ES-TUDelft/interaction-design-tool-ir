from es_common.model.interaction_block import InteractionBlock
from es_common.model.observable import Observable

block_observers = Observable()


def create_block_parent(parent_data, hashmap={}):
    interaction_block = InteractionBlock.create_interaction_block(parent_data)
    # deserialize
    interaction_block.deserialize(parent_data, hashmap)

    block_observers.notify_all(interaction_block.block)

    return interaction_block
