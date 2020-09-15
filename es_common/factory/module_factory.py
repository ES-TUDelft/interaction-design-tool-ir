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
    def create_module(module_type_key, *args):
        new_module = None

        try:
            if module_type_key not in InteractionModule.keys():
                return new_module

            module_class = ModuleFactory.get_class(
                module_name="es_common.module.{}_module".format(module_type_key.lower()),
                class_name="{}Module".format(InteractionModule[module_type_key].value))

            new_module = module_class(*args)

        except Exception as e:
            ModuleFactory.logger.error("Error while creating module: {} | {}".format(module_type_key, e))
        finally:
            return new_module

    @staticmethod
    def get_class(module_name, class_name):
        the_class = None
        try:
            the_class = getattr(importlib.import_module(module_name), class_name)
        except Exception as e:
            ModuleFactory.logger.error("Error while creating class for: {} | {} | {}".format(
                module_name, class_name, e))
        finally:
            return the_class
