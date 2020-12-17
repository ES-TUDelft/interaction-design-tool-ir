#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============ #
# MAIN_MONGODB #
# ============ #
# Class for accessing MongoDB
#
# @author ES
# **
import os

from data_manager.dao.mongo_dao import MongoDAO
from es_common.utils.csv_helper import CSVHelper
import time


def main():
    mongodb = MongoDAO()
    success = mongodb.connect()
    print('Success = {}'.format(success))

    # delete_databases(mongodb, db_names = mongodb.get_all_databases())

    db_names = mongodb.get_all_databases()
    # print("DBs: {}".format(db_names))
    for db_name in db_names:
        if 'Interaction_DB' in db_name:
            get_dialogues(mongodb, db_name)


def delete_databases(mongodb, db_names):
    for db_name in db_names:
        if 'HRE_' in db_name:
            mongodb.delete_database(db_name)
    print("Remaining DBs: {}".format(mongodb.get_all_databases()))


def get_dialogues(mongodb, db_name):
    mongodb.set_database(db_name=db_name)
    dialogues = mongodb.get_dialogue_designs()
    # print(dialogues)

    # TODO
    write_blocks_as_csv(db_name, dialogues)
    read_csv_data(db_name)

    '''
    for dialog in dialogues:
        print(dialog.keys())
        print(dialog['_id'])
        print(dialog['communication_style'])
        print(dialog['blocks']["{}".format(0)].keys())

        for x in range(len(dialog['blocks'])):
            print(x)
            print(dialog['blocks']["{}".format(x)])
    '''


def write_blocks_as_csv(db_name, dialogues):
    main_fieldnames = ['_id', 'date', 'time', 'communication_style']
    blocks_fieldnames = ['block_number', 'name', 'message', 'execution_result',
                         'start_time', 'end_time', 'interaction_time']

    fieldnames = []
    fieldnames.extend(main_fieldnames)
    fieldnames.extend(blocks_fieldnames)

    csv_helper = CSVHelper()
    csv_helper.set_csv_writer(fieldnames=fieldnames, filename=create_filename(db_name))

    for dialog in dialogues:
        to_row = {'_id': dialog['_id'],
                  'date': time.strftime("%D", time.localtime(dialog['time'])),
                  'time': time.strftime("%T", time.localtime(dialog['time'])),
                  'communication_style': dialog['communication_style']}

        # get each block as a new row
        blocks = dialog['blocks']
        # row numbers are the keys
        for i in range(len(blocks.keys())):
            row = {}
            row.update(to_row)
            b = blocks['{}'.format(i)]

            row['block_number'] = i
            row['name'] = b['name']
            row['message'] = b['speech_act']["message"]
            row['execution_result'] = b['execution_result']
            row['start_time'] = b['interaction_start_time']
            row['end_time'] = b['interaction_end_time']
            row['interaction_time'] = b['interaction_end_time'] - b['interaction_start_time']

            csv_helper.write(row)


def create_filename(db_name):
    cwd = "{}/logs/csv".format(os.getcwd())
    return '{}/{}_dialogBlocks'.format(cwd, db_name)


def read_csv_data(db_name):
    csv_helper = CSVHelper()
    data = csv_helper.read(directory="", filename=create_filename(db_name))

    if data is not None and len(data) > 0:
        print(data[0])


def write_raw_blocks_as_csv(db_name, dialogues):
    main_fieldnames = ['_id', 'time', 'communication_style']
    blocks_fieldnames = []
    blocks_fieldnames.extend(dialogues[0]['blocks']["{}".format(0)].keys())

    fieldnames = []
    fieldnames.extend(main_fieldnames)
    fieldnames.append('row')
    fieldnames.extend(blocks_fieldnames)

    csv_helper = CSVHelper()
    csv_helper.set_csv_writer(fieldnames=fieldnames, filename='{}_dialogBlocks'.format(db_name))

    for dialog in dialogues:
        to_row = {}
        for k in main_fieldnames:
            to_row[k] = dialog[k]

        # get each block as a new row
        blocks = dialog['blocks']
        # row numbers are the keys
        for i in range(len(blocks.keys())):
            row = {}
            row.update(to_row)
            row['row'] = i
            row.update(blocks['{}'.format(i)])
            csv_helper.write(row)


if __name__ == '__main__':
    main()
