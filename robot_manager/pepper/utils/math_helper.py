#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# MATH_HELPER #
# =========== #
# Helper class for math functionalities
#
# @author ES
# **

import numpy as np


def compute_rms_level(data):
    """
    Returns RMS
    """
    rms = 20 * np.log10(np.sqrt(np.sum(np.power(data, 2) / len(data))))
    return rms


def convert_string_to_signed_int(data):
    """
    This function takes a string containing 16 bits little endian sound
    samples as input and returns a vector containing the 16 bits sound
    samples values converted between -1 and 1.
    """
    signed_data = []
    ind = 0
    for i in range(0, len(data) / 2):
        signed_data.append(data[ind] + data[ind + 1] * 256)
        ind = ind + 2

    for i in range(0, len(signed_data)):
        if signed_data[i] >= 32768:
            signed_data[i] = signed_data[i] - 65536

    for i in range(0, len(signed_data)):
        signed_data[i] = signed_data[i] / 32768.0

    return signed_data


def get_peak_and_sound_data(audio_buffer, channels, samples_by_channel):
    sound_data_interlaced = np.fromstring(str(audio_buffer), dtype=np.int16)
    sound_data = np.reshape(sound_data_interlaced, (channels, samples_by_channel), 'F')
    return np.max(sound_data), sound_data
