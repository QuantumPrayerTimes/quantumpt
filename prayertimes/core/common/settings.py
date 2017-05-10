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

from PyQt5.QtCore import QSettings

from prayertimes.core.common.logapi import log
from prayertimes.core.common.registry import Registry

from prayertimes.utils.date_timezone import get_utc_offset


class Settings(QSettings):
    """
    Class to wrap QSettings.
    """

    default_config = {
        'city/continent': 'Europe',
        'city/country': 'France',
        'city/cc': 'FR',
        'city/city': 'Paris',
        'city/state': 'Ile-de-France',
        'city/latitude': 49.25,
        'city/longitude': 4.03,
        'city/timezone': 'Europe/Paris',
        'city/utc': 2,
        'prayer_offsets/fajr': 0,
        'prayer_offsets/shourouq': 0,
        'prayer_offsets/dhuhr': 0,
        'prayer_offsets/asr': 0,
        'prayer_offsets/maghrib': 0,
        'prayer_offsets/isha': 0,
        'prayer_settings/asr_method': 'standard',
        'prayer_settings/calculation': 'ISNA',
        'prayer_settings/dua_after_athan': 1,
        'general_settings/arabic_names': 0,
        'general_settings/wizard_runned': 0,
        'general_settings/close': 0,
        'general_settings/splashscreen': 1,
        'general_settings/language': 'en_US',
    }

    current_config = {}

    file_path = 'settings.ini'

    def __init__(self):
        super(Settings, self).__init__(self.file_path, QSettings.IniFormat)
        QSettings().setFallbacksEnabled(False)  # File only, no fallback to registry.

        Registry().register_function("restore_default_settings", self.set_up_default_values)

    def save_city_config(self, city_dict):
        """
        Save settings concerning the city configuration.

        :param city_dict:
        :return:
        """
        log.debug("saving city config: \n{}".format(city_dict))
        self.setValue("city/continent", city_dict["continent"])
        self.setValue("city/country", city_dict["country"])
        self.setValue("city/cc", city_dict["cc"].lower())
        self.setValue("city/city", city_dict["city"])
        self.setValue("city/state", city_dict["state"])
        self.setValue("city/latitude", city_dict["lat"])
        self.setValue("city/longitude", city_dict["lng"])
        self.setValue("city/timezone", city_dict["tz"])
        self.setValue("city/utc", get_utc_offset(city_dict["tz"]))

    def load_city_config(self):
        """
        Load settings concerning the city configuration.

        :return:
        """
        city_dict = dict(city=self.value("city/city", type=str),
                         continent=self.value("city/continent", type=str),
                         country=self.value("city/country", type=str),
                         cc=self.value("city/cc", type=str),
                         state=self.value("city/state", type=str),
                         lat=self.value("city/latitude", type=float),
                         lng=self.value("city/longitude", type=float),
                         tz=self.value("city/timezone", type=str),
                         utc=self.value("city/utc", type=float)
                         )

        log.debug("loading city config: \n{}".format(city_dict))
        return city_dict

    def save_prayer_offsets_config(self, prayer_offsets):
        """
        Save settings concerning the prayer offsets.

        :param prayer_offsets:
        :return:
        """
        log.debug("saving prayer offsets: \n{}".format(prayer_offsets))
        for p_name, offset in prayer_offsets.items():
            self.setValue("prayer_offsets/{}".format(p_name.lower()), offset)

    @staticmethod
    def set_filename(ini_file):
        """
        Sets the complete path to an Ini file to be used by Settings objects.
        Does not affect existing Settings objects.

        :param ini_file: the name of .ini file
        :return:
        """
        Settings.file_path = ini_file

    def set_up_default_values(self):
        """
        This static method is called on start up.
        It is used to perform any operation on the default_config dict.

        :return:
        """
        log.debug("setting default settings values:")
        for key, value in self.default_config.items():
            self.setValue(key, value)
        self.sync()

    @property
    def current_settings(self):
        """
        Get the current configuration.

        :return:
        """
        self.current_config.update(self._get_current_configuration())
        return self.current_config

    def _get_current_configuration(self):
        """
        Generate the current configuration.

        :return:
        """
        setting_keys = self.allKeys()
        current_configuration = {}
        for key in setting_keys:
            current_configuration[key] = self.value(key)
        return current_configuration

    def extend_current_settings(self):
        """
        Extend the current configuration with default configuration in case it is incomplete.

        :return:
        """
        self.default_config.update(self.current_settings)
        for key, value in self.default_config.items():
            self.setValue(key, value)
        self.sync()

    def update_current_settings(self, settings_dict):
        """
        Update the current configuration with dictionnary parameter.

        :param settings_dict:
        :return:
        """
        assert isinstance(settings_dict, dict)

        for key, value in settings_dict.items():
            self.setValue(key, value)
        self.sync()

    def get_default_value(self, key):
        """
        Get the default value of the given key.

        :param key: the key we want its default value.
        :return: the default value of the key given in parameter.
        """
        if self.group():
            key = self.group() + '/' + key
        return Settings.default_config[key]

    def value(self, key, **kwargs):
        """
        Returns the value for the given ``key``. The returned ``value`` is of the same
        type as the default value in the *Settings.default_config* dict.

        :param key: The key to return the value from.
        :return:
        """
        # if group() is not empty the group has not been specified together with the key.
        if self.group():
            default_value = Settings.default_config[self.group() + '/' + key]
        else:
            default_value = Settings.default_config[key]
        setting = super(Settings, self).value(key, default_value, **kwargs)
        return self._convert_value(setting, default_value)

    @staticmethod
    def _convert_value(setting, default_value):
        """
        This converts the given ``setting`` to the type of the given ``default_value``.

        :param setting: The setting to convert. This could be ``true`` for example.Settings()
        :param default_value: Indication the type the setting should be converted to. For example ``True``
        (type is boolean), meaning that we convert the string ``true`` to a python boolean.

        **Note**, this method only converts a few types and might need to be extended if a certain type is missing!
        """
        # Handle 'None' type (empty value) properly.
        if setting is None:
            # An empty string saved to the settings results in a None type being returned.
            # Convert it to empty unicode string.
            if isinstance(default_value, str):
                return ''
            # An empty list saved to the settings results in a None type being returned.
            else:
                return []
        # Convert the setting to the correct type.
        if isinstance(default_value, bool):
            if isinstance(setting, bool):
                return setting
            # Sometimes setting is string instead of a boolean.
            return setting == 'true'
        if isinstance(default_value, int):
            return int(setting)
        if isinstance(default_value, float):
            return float(setting)
        return setting
