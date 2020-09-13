#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ========= #
# IP_HELPER #
# ========= #
# Helper class
#
# @author ES
# **

import logging
import socket

logger = logging.getLogger("IPHelper")


def get_host_ip():
    address = ""
    try:
        ips = socket.gethostbyname_ex(socket.gethostname())
        # ips has the following structure: ('pc name', [], ['0.0.0.0'])
        logger.info(ips)
        for ip in ips[2]:
            if ip.startswith("192."):  # not ip.startswith("127."):
                address = ip
                break
        if address is None or address == '':
            socket_object = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_object.connect(("4.2.2.1", 0))
            address = socket_object.getsockname()[0]
    except Exception as e:
        logger.error("Error while getting the ip! {}".format(e))
    finally:
        return address
