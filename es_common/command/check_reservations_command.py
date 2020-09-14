#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======================== #
# CHECK_RESERVATIONS_COMMAND #
# ======================== #
# Command for checking reservations.
#
# @author ES
# **
import logging
from collections import OrderedDict

from es_common.command.es_command import ESCommand
from es_common.enums.command_enums import ActionCommand


class CheckReservationsCommand(ESCommand):
    def __init__(self, is_speech_related=False):
        super(CheckReservationsCommand, self).__init__(is_speech_related=is_speech_related)

        self.logger = logging.getLogger("GetReservations Command")
        self.command_type = ActionCommand.CHECK_RESERVATIONS

    # =======================
    # Override Parent methods
    # =======================
    def execute(self):
        success = False
        try:
            self.logger.info("Not implemented!")

        except Exception as e:
            self.logger.error("Error while checking the reservation! {}".format(e))
        finally:
            return success

    def reset(self):
        pass

    def clone(self):
        return CheckReservationsCommand()

    ###
    # SERIALIZATION
    ###
    def serialize(self):
        return OrderedDict([
            ("id", self.id),
            ("command_type", self.command_type.name)
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data["id"]
        hashmap[data["id"]] = self

        return True
