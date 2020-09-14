from es_common.model.reservation import Reservation


def create_reservations_list(res_json):
    res_lst = []
    for res in res_json:
        if res and "customer" in res.keys():
            try:
                res_lst.append(Reservation.create_reservation(res))
                # print(json.dumps(reservation["customer"], indent=2))
            except Exception as e:
                print("Error while getting reservations data: {}".format(e))
            finally:
                continue
    return res_lst


def get_customers_names(res_json):
    firstnames = []
    lastnames = []
    for res in res_json:
        if res and "customer" in res.keys():
            firstnames.append(res["customer"]["firstname"])
            lastnames.append(res["customer"]["lastnames"])

    return firstnames, lastnames


def get_customers_prop(res_json, prop_key="firstname"):
    prop_lst = []
    for res in res_json:
        if res and "customer" in res.keys():
            prop_lst.append(res["customer"][prop_key])

    return prop_lst
