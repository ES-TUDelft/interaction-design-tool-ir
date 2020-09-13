#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# CSV_HELPER #
# =========== #
# Helper class for reading/writing csv files
#
# @author ES
# **

import csv
import logging
import os
import time


class CSVHelper:

    def __init__(self):
        self.logger = logging.getLogger("CSVHelper")
        self.csv_writer = None

    def set_csv_writer(self, fieldnames, filename=None, output_dir=""):
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError:
                pass

        csv_file = open('{}/{}.csv'.format(output_dir, get_file_name() if filename is None else filename),
                        'w')  # , encoding='utf-8-sig')
        self.csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        self.csv_writer.writeheader()

    def write(self, row=None):
        if self.csv_writer is None:
            self.logger.error('*** No csv writer defined - Set csv writer before proceeding.')

        if row is not None:
            self.csv_writer.writerow(row)

    def read(self, directory=None, filename=None):
        if filename is None: return None
        reader = None
        try:
            file_path = filename if directory is None else "{}/{}.csv".format(directory, filename)
            with open(file_path) as csv_file:
                # csv_file = open(filename if '.csv' in filename else '{}.csv'.format(filename), 'r',
                # encoding='utf-8-sig')
                reader = list(csv.DictReader(csv_file))
        except csv.Error as e:
            self.logger.error('Error while opening the file {} - {}'.format(filename, e))
        finally:
            return reader


def get_file_name():
    return 'log_{}'.format(time.strftime("%a%d%b%Y_%H:%M:%S", time.localtime()))


def export_blocks(filename, foldername, dialogue_design):
    message = None
    error = None
    try:
        if dialogue_design is None or len(dialogue_design.blocks) == 0:
            f = open("{}/{}.csv".format(foldername, filename), "w")
            f.truncate()
            f.close()
            message = "Successfully emptied the csv file"
        else:
            fieldnames = ['_id', 'date', 'time', 'row', 'name', 'stage', 'interaction_time', 'message', 'chat_topic']
            fieldnames.extend(dialogue_design.blocks["{}".format(0)]['behavioral_parameters'].keys())
            fieldnames.remove('voice')
            voice_fieldnames = ['volume', 'pitch', 'speed', 'prosody']
            fieldnames.extend(voice_fieldnames)

            csv_helper = CSVHelper()
            csv_helper.set_csv_writer(fieldnames=fieldnames, output_dir=foldername, filename=filename)

            to_row = {'_id': time.time(), 'date': time.strftime("%D", time.localtime(dialogue_design.time)),
                      'time': time.strftime("%T", time.localtime(dialogue_design.time))}

            # get each block as a new row
            blocks = dialogue_design.blocks
            # row numbers are the keys
            for i in range(len(blocks.keys())):
                row = {}
                row.update(to_row)
                row['row'] = i
                b = blocks['{}'.format(i)]
                row['name'] = b['name']
                row['stage'] = b['stage'] if 'stage' in b.keys() else ""
                row['interaction_time'] = b['interaction_end_time'] - b['interaction_start_time']
                row['chat_topic'] = b['topic_tag']['topic']
                row.update(b['behavioral_parameters'])
                row.pop('voice', None)
                for k in voice_fieldnames:
                    row[k] = b['behavioral_parameters']['voice'][k]
                csv_helper.write(row)
                message = "Successfully exported the blocks."
    except Exception as e:
        error = "Error while exporting the blocks: {}".format(e)
    finally:
        return message, error
