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


class ModuleFactory(object):
    logger = logging.getLogger("ModuleFactory")

    @staticmethod
    def create_module(module_type, *args):
        new_module = None

        try:
            module_class = ModuleFactory.get_class(
                module_name="es_common.module.{}_module".format(module_type.name.lower()),
                class_name="{}Module".format(module_type.value))

            new_module = module_class(*args)

        except Exception as e:
            ModuleFactory.logger.error("Error while creating module: {} | {}".format(module_type, e))
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
