from collections import OrderedDict

from es_common.model.customer import Customer


class Reservation(object):
    def __init__(self, res_id, customer, guests, table, time):
        self.id = res_id
        self.customer = customer
        self.guests = guests
        self.table = table
        self.time = time

    @property
    def to_dict(self):
        res_dict = OrderedDict([
            ("id", self.id),
            ("customer", self.customer.to_dict),
            ("guests", self.guests),
            ("table", self.table),
            ("time", self.time)
        ])
        return res_dict

    @staticmethod
    def create_reservation(res_dict):
        if res_dict:
            try:
                table = res_dict["table"] if "table" in res_dict.keys() else res_dict["table_string"]
                reservation = Reservation(res_id=res_dict["id"],
                                          customer=Customer.create_customer(res_dict["customer"]),
                                          guests=res_dict["guests"],
                                          table=table,
                                          time=res_dict["time"])
                return reservation
            except Exception as e:
                self.logger.error("Error while creating reservation from {} | {}".format(res_dict, e))

        return None
