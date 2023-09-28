#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------- #
# QuantumPT - Open Source Portable Islamic prayer times reminder              #
# --------------------------------------------------------------------------- #
# Copyright (c) 2016 QuantumPT Developer                                      #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 3 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
# --------------------------------------------------------------------------- #
# Some functions present in this file has been originally used in OpenLP      #
# project : https://openlp.org                                                #
# --------------------------------------------------------------------------- #

import sys

from prayertimes.core.common import trace_error_handler
from prayertimes.core.common.logapi import log


class Registry(object):
    """
    This is the Component Registry. It is a singleton object and is used to
    provide a look up service for common objects.
    """

    log.info("Registry loaded")
    __instance__ = None

    def __new__(cls):
        """
        Re-implement method __new__ to have a singleton.
        """
        if not cls.__instance__:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    @classmethod
    def create(cls):
        """
        The constructor for the component registry providing a single registry of objects.
        """
        log.debug("Registry Initialising")
        # registry = cls()
        cls.service_list = {}
        cls.functions_list = {}
        cls.signals_list = {}
        # Allow the tests to remove Registry entries but not the live system
        cls.running_under_test = "nose" in sys.argv[0]
        cls.initialising = True
        return cls

    def get(self, key):
        """
        Extracts the registry value from the list based on the key passed in.

        :param key: The service to be retrieved.
        """
        if key in self.service_list:
            return self.service_list[key]
        else:
            if not self.initialising:
                trace_error_handler(log)
                log.error("Service %s not found in list" % key)
                raise KeyError("Service %s not found in list" % key)

    def register(self, key, reference):
        """
        Registers a component against a key.

        :param key: The service to be created this is usually a major class like "global_frame" .
        :param reference: The service address to be saved.
        """
        if key in self.service_list:
            trace_error_handler(log)
            log.error("Duplicate service exception %s" % key)
            raise KeyError("Duplicate service exception %s" % key)
        else:
            self.service_list[key] = reference

    def remove(self, key):
        """
        Removes the registry value from the list based on the key passed in
        (Only valid and active for testing framework).

        :param key: The service to be deleted.
        """
        if key in self.service_list:
            del self.service_list[key]

    def register_function(self, event, _function):
        """
        Register an event and associated function to be called.

        :param event: The function description.
        :param _function: The function to be called when the event happens.
        """
        if event in self.functions_list:
            self.functions_list[event].append(_function)
        else:
            self.functions_list[event] = [_function]

    def remove_function(self, event, _function):
        """
        Remove an event and associated handler.

        :param event: The function description.
        :param _function: The function to be called when the event happens.
        """
        if event in self.functions_list:
            self.functions_list[event].remove(_function)

    def execute(self, event, *args, **kwargs):
        """
        Execute all the handlers associated with the event and return an array of results.

        :param event: The function to be processed.
        :param args: Parameters to be passed to the function.
        :param kwargs: Parameters to be passed to the function.
        """
        results = []
        if event in self.functions_list:
            for _function in self.functions_list[event]:
                try:
                    result = _function(*args, **kwargs)
                    if result:
                        results.append(result)
                except TypeError:
                    trace_error_handler(log)
                    log.exception("Exception for function %s", _function)
        else:
            trace_error_handler(log)
            log.error("Event %s called but not registered" % event)
        return results

    def register_signal(self, event, signal):
        """
        Register an event and associated pyqt signal to be called.

        :param event: The signal description.
        :param signal: The signal to be emitted when the event happens.
        """
        if event in self.signals_list:
            self.signals_list[event].append(signal)
        else:
            self.signals_list[event] = [signal]

    def emit_signal(self, event, *args, **kwargs):
        """
        Execute all the handlers associated with the event and return an array of results.

        :param event: The signal to be processed.
        :param args: Parameters to be passed to the signal.
        :param kwargs: Parameters to be passed to the signal.
        """
        results = []
        if event in self.signals_list:
            for signal in self.signals_list[event]:
                try:
                    result = signal.emit(*args, **kwargs)
                    if result:
                        results.append(result)
                except TypeError:
                    trace_error_handler(log)
                    log.exception("Exception for signal %s", signal)
        else:
            trace_error_handler(log)
            log.error("Signal %s called but not registered" % event)
        return results
