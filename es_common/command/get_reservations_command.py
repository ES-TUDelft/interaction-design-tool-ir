#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ======================== #
# GET_RESERVATIONS_COMMAND #
# ======================== #
# Command for wait action.
#
# @author ES
# **
import base64
import logging
from collections import OrderedDict

import requests

from es_common.command.es_command import ESCommand
from es_common.enums.command_enums import ActionCommand
from es_common.utils import config_helper, date_helper


class GetReservationsCommand(ESCommand):
    def __init__(self, is_speech_related=False):
        super(GetReservationsCommand, self).__init__(is_speech_related=is_speech_related)

        self.logger = logging.getLogger("GetReservations Command")
        self.command_type = ActionCommand.GET_RESERVATIONS

    # =======================
    # Override Parent methods
    # =======================
    def execute(self):
        reservations = []
        try:
            table_booker = config_helper.get_table_booker_settings()

            # Set the token
            token = "{}:{}".format(table_booker["username"], table_booker["password"])
            token = base64.b64encode(token.encode("utf-8")).decode("utf-8")
            table_booker["headers"]["Authorization"] = "Basic {}".format(token)

            # Update the date
            table_booker["params"]["from_date"] = date_helper.get_today_date()
            table_booker["params"]["to_date"] = date_helper.get_tomorrow_date()
            # self.logger.info(table_booker)

            # Get reservations
            response = requests.get(table_booker["reservations_url"],
                                    headers=table_booker["headers"], params=table_booker["params"])

            # self.logger.info(response.json())
            if "reservations" in response.json().keys():
                success = True
                reservations = response.json()["reservations"]

                # self.logger.debug(json.dumps(reservations, indent=2))
                self.logger.info("Execution was successful. Found {} reservation(s)\n".format(len(reservations)))

        except Exception as e:
            self.logger.error("Error while fetching the reservations! {}".format(e))
        finally:
            return reservations  # json

    def reset(self):
        pass

    def clone(self):
        return GetReservationsCommand()

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
