import logging
from collections import OrderedDict

from es_common.command.get_reservations_command import GetReservationsCommand
from es_common.enums.module_enums import InteractionModule
from es_common.model.customer import Customer
from es_common.model.reservation import Reservation
from es_common.module.es_interaction_module import ESInteractionModule

INT_DESIGN_FILE = "es_common/module/interaction_design/reservations.json"


class RestaurantReservationsModule(ESInteractionModule):
    def __init__(self, origin_block, block_controller=None):
        super().__init__(block_controller, origin_block)
        self.logger = logging.getLogger("RestaurantReservationsModule")

        self.module_type = InteractionModule.RESTAURANT_RESERVATIONS
        self.design_file = INT_DESIGN_FILE

        self.reservations = []
        self.current_reservation = Reservation()
        self.current_customer = Customer()
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
            # update keywords
            keywords = self.next_int_block.answers
            firstnames, lastnames = self.get_customers_names()

            if len(firstnames) > 0:
                for i in range(len(keywords)):
                    if "{firstnames}" in keywords[i]:
                        keywords[i] = keywords[i].format(firstnames=";".join(firstnames))

                self.next_int_block.answers = keywords
                self.logger.info("Keywords are set to: {}".format(self.next_int_block.answers))
            else:
                self.logger.info("Couldn't get the keywords!")

            # update message
            message = self.next_int_block.message
            if message:
                if self.execution_result:
                    if "{firstname}" in message:
                        self.logger.info("Firstname: {}".format(self.execution_result))
                        self.current_customer.firstname = self.execution_result
                        message = message.replace("{firstname}", self.current_customer.firstname)
                        indexes = [i for i in range(len(firstnames)) if
                                   firstnames[i].lower() == self.current_customer.firstname.lower()]
                        if len(indexes) > 0:
                            self.current_customer.lastname = lastnames[indexes[0]]
                            self.logger.info("Lastname: {}".format(self.current_customer.lastname))
                        else:
                            self.current_customer.lastname = ""
                        message = message.replace("{lastname}", self.current_customer.lastname)
                        # message.format(firstname=self.current_customer.firstname,
                        # lastname=self.current_customer.lastname)
                        self.update_current_reservation()

                if "{reservation_table}" in message:
                    message = message.replace("{reservation_table}", "{}".format(self.current_reservation.table))
                if "{reservation_guests}" in message:
                    message = message.replace("{reservation_guests}", "{}".format(self.current_reservation.guests))
                if "{reservation_time}" in message:
                    message = message.replace("{reservation_time}", "{}".format(self.current_reservation.time))

                self.next_int_block.message = message
                self.logger.info("Filled in the reservation and updated the message to: {}".format(
                    self.next_int_block.message))

    def update_current_reservation(self):
        if self.current_customer.firstname:
            for res in self.reservations:
                try:
                    firstname = res["customer"]["firstname"]
                    lastname = res["customer"]["lastname"]
                    if firstname.lower() == self.current_customer.firstname.lower() \
                            and lastname.lower() == self.current_customer.lastname.lower():
                        self.current_reservation.id = res["id"]
                        self.current_reservation.customer = self.current_customer
                        self.current_reservation.guests = res["guests"]
                        self.current_reservation.table = res["table"] if "table" in res.keys() else res["table_string"]
                        self.current_reservation.time = res["time"]
                except Exception as e:
                    self.logger.error("Error while checking reservations. {}".format(e))

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
