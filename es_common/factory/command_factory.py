#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# =========== #
# COMMAND_FACTORY #
# =========== #
# Factory for creating commands.
#
# @author ES
# **
import importlib
import logging


class CommandFactory(object):
    logger = logging.getLogger("CommandFactory")

    @staticmethod
    def create_command(command_type, *args):
        new_command = None

        try:
            command_class = CommandFactory.get_class(
                module_name="es_common.command.{}_command".format(command_type.name.lower()),
                class_name="{}Command".format(command_type.value))

            new_command = command_class(*args)

            # if command_type is ActionCommand.DRAW_NUMBER:
            #     new_command = DrawNumberCommand(*args)

        except Exception as e:
            CommandFactory.logger.error("Error while creating command: {} | {}".format(command_type, e))
        finally:
            return new_command

    @staticmethod
    def get_class(module_name, class_name):
        the_class = None
        try:
            the_class = getattr(importlib.import_module(module_name), class_name)
        except Exception as e:
            CommandFactory.logger.error("Error while creating class for: {} | {} | {}".format(
                module_name, class_name, e))
        finally:
            return the_class
