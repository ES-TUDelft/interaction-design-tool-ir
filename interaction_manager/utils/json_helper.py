#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# JSON_HELPER #
# =========== #
# Helper class for reading/writing JSON files.
#
# @author ES
# **

import json
from collections import OrderedDict


def export_blocks(filename, foldername, interaction_design):
    message = None
    error = None
    try:
        if interaction_design is None or len(interaction_design.blocks) == 0:
            f = open("{}/{}.json".format(foldername, filename), "w")
            f.truncate()
            f.close()
            message = "Successfully emptied: {}/{}.json".format(foldername, filename)
        else:
            with open("{}/{}.json".format(foldername, filename), "w") as fp:
                json.dump(interaction_design.blocks, fp, indent=4, sort_keys=False)
                message = "Successfully exported the blocks."
    except Exception as e:
        error = "Error while exporting the blocks: {}".format(e)
    finally:
        return message, error


def import_blocks(filename, foldername=None):
    error = None
    blocks_data = None
    try:
        file_path = filename if foldername is None else "{}/{}.json".format(foldername, filename)
        with open(file_path) as json_file:
            blocks_data = json.load(json_file, object_pairs_hook=OrderedDict)
    except Exception as e:
        error = "Error while reading the json file: {} | {}".format(filename, e)
    finally:
        return blocks_data, error
