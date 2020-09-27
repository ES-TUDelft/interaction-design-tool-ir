#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **
#
# ============== #
# MODULE_FACTORY #
# ============== #
# Factory for creating modules.
#
# @author ES
# **
import importlib
import logging

from es_common.enums.module_enums import InteractionModule


class ModuleFactory(object):
    logger = logging.getLogger("ModuleFactory")

    @staticmethod
    def create_module(design_module, *args):
        if design_module is None:
            return None

        interaction_module = None

        try:
            folder_name = "es_common.module.{}_module"
            class_name = "{}Module"
            if design_module.name in InteractionModule.keys():
                folder_name = folder_name.format(design_module.name.lower())
                class_name = class_name.format(InteractionModule[design_module.name.upper()].value)
            else:
                folder_name = folder_name.format("es_interaction")
                class_name = class_name.format("ESInteraction")

            module_class = ModuleFactory.get_class(folder_name=folder_name, class_name=class_name)

            interaction_module = module_class(*args)

        except Exception as e:
            ModuleFactory.logger.error("Error while creating module: {}".format(e))
        finally:
            return interaction_module

    @staticmethod
    def get_class(folder_name, class_name):
        the_class = None
        try:
            the_class = getattr(importlib.import_module(folder_name), class_name)
        except Exception as e:
            ModuleFactory.logger.error("Error while creating class for: {} | {} | {}".format(
                folder_name, class_name, e))
        finally:
            return the_class
