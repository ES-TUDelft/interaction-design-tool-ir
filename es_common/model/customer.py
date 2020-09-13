import logging
from collections import OrderedDict


class Customer(object):
    def __init__(self, customer_id, firstname, lastname):
        self.logger = logging.getLogger("Customer")
        self.id = customer_id
        self.firstname = firstname
        self.lastname = lastname

    @property
    def to_dict(self):
        customer_dict = OrderedDict([
            ("id", self.id),
            ("firstname", self.firstname),
            ("lastname", self.lastname)
        ])
        return customer_dict

    @staticmethod
    def create_customer(customer_dict):
        if customer_dict:
            try:
                customer = Customer(customer_id=customer_dict["id"],
                                    firstname=customer_dict["firstname"],
                                    lastname=customer_dict["lastname"])
                return customer
            except Exception as e:
                print("Error while creating customer from {} | {}".format(customer_dict, e))

        return None
