import logging
from collections import OrderedDict

from es_common.command.get_reservations_command import GetReservationsCommand
from es_common.enums.module_enums import InteractionModule
from es_common.module.es_module import ESModule

INT_DESIGN_FILE = "es_common/module/interaction_design/reservations.json"


class RestaurantReservationsModule(ESModule):
    def __init__(self, block_controller, origin_block=None):
        super().__init__(block_controller, origin_block)
        self.logger = logging.getLogger("RestaurantReservationsModule")

        self.module_type = InteractionModule.RESTAURANT_RESERVATIONS
        self.design_file = INT_DESIGN_FILE

        self.reservations = []
        self.current_reservation = None
        self.get_reservations_command = GetReservationsCommand()

    def start_module(self):
        self.reservations = self.get_reservations_command.execute()

        if self.reservations and len(self.reservations) > 0:
            # get names
            firstnames, lastnames = self.get_customers_names()
            self.logger.info(f"{firstnames} | {lastnames}")
            return True

        return False

    def update_next_block_fields(self):
        if self.next_int_block:
            keywords = self.next_int_block.answers
            firstnames, _ = self.get_customers_names()

            for i in range(len(keywords)):
                if "{firstnames}" in keywords[i]:
                    keywords[i] = keywords[i].format(firstnames=";".join(firstnames))

            self.next_int_block.answers = keywords
            self.logger.info("Keywords are set to: {}".format(self.next_int_block.answers))

    def get_customers_names(self):
        firstnames = []
        lastnames = []

        for res in self.reservations:
            try:
                if res and "customer" in res.keys():
                    firstnames.append(res["customer"]["firstname"])
                    lastnames.append(res["customer"]["lastname"])
            except Exception as e:
                self.logger.error("Error while fetching customers: {}".format(e))
            finally:
                continue

        return firstnames, lastnames

    ###
    # SERIALIZATION
    ###
    def serialize(self):
        return OrderedDict([
            ("id", self.id),
            ("module_type", self.module_type.name)
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data["id"]
        hashmap[data["id"]] = self

        return True
