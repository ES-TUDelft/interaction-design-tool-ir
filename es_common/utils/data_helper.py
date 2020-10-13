import logging
import json
import os
from collections import OrderedDict

logger = logging.getLogger("File_Helper")


def save_to_file(filename, serialized_data):
    try:
        with open(filename, "w") as w_file:
            json.dump(serialized_data, w_file, indent=4, sort_keys=False)
            logger.info("Successfully saved data to '{}'".format(filename))
    except (IOError, Exception) as e:
        logger.error("Error while writing to '{}' | {}".format(filename, e))


def load_data_from_file(filename):
    data = None
    try:
        with open(filename, "r") as r_file:
            data = json.loads(r_file.read(), object_pairs_hook=OrderedDict, encoding="utf-8")
            logger.info("Successfully loaded data from '{}'".format(filename))
    except (IOError, Exception) as e:
        logger.error("Error while loading data from file {} : {}".format(filename, e))
    finally:
        return data


def get_backup_filename():
    return "{}/logs/interaction.json".format(os.getcwd())


# HELPER METHOD
# =============
def join_array(arr, to_split=";"):
    if arr is None or len(arr) == 0:
        return []

    result = []
    for i in range(len(arr)):
        keywords = [s.strip() for s in arr[i].split(to_split) if s.strip() != '']
        result.extend(keywords)
    # print("Result from join: {}".format(result))
    return result
