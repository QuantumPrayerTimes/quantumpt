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

from collections import OrderedDict

from prayertimes.utils.date_timezone import get_utc_offset


class City:
    """
    Basic class for city informations.

    This may evolve later to take into account multiple favorite cities defined by users.
    """

    # __instance__ = None
    #
    # def __new__(cls, city_dict):
    #     """
    #     Re-implement method __new__ to have a singleton.
    #     """
    #     if not cls.__instance__:
    #         cls.__instance__ = object.__new__(cls)
    #     return cls.__instance__

    def __init__(self, city_dict):
        """
        Initialize class attributes.

        :param city_dict:
        """
        if not isinstance(city_dict, dict):
            raise TypeError("Argument must be a dictionnary")

        if city_dict:
            # Convert values to string to get a readable format.
            city_dict = {k: str(v) for k, v in city_dict.items()}

            _city = (
                ("continent", city_dict["continent"]),
                ("country", city_dict["country"]),
                ("cc", city_dict["cc"]),
                ("state", city_dict["state"]),
                ("city", city_dict["city"]),
                ("lat", city_dict["lat"]),
                ("lng", city_dict["lng"]),
                ("tz", city_dict["tz"]),
                ("utc", get_utc_offset(city_dict["tz"])),
            )

            self._city_info = OrderedDict(_city)
        else:
            self._city_info = OrderedDict()

    @property
    def continent(self):
        return self._city_info["continent"]

    @continent.setter
    def continent(self, value):
        self._city_info["continent"] = value

    @property
    def country(self):
        return self._city_info["country"]

    @country.setter
    def country(self, value):
        self._city_info["country"] = value

    @property
    def state(self):
        return self._city_info["state"]

    @state.setter
    def state(self, value):
        self._city_info["state"] = value

    @property
    def city(self):
        return self._city_info["city"]

    @city.setter
    def city(self, value):
        self._city_info["city"] = value

    @property
    def lat(self):
        return float(self._city_info["lat"])

    @lat.setter
    def lat(self, value):
        self._city_info["lat"] = value

    @property
    def lng(self):
        return float(self._city_info["lng"])

    @lng.setter
    def lng(self, value):
        self._city_info["lng"] = value

    @property
    def tz(self):
        return self._city_info["tz"]

    @tz.setter
    def tz(self, value):
        self._city_info["tz"] = value

    @property
    def cc(self):
        return self._city_info["cc"]

    @cc.setter
    def cc(self, value):
        self._city_info["cc"] = value

    @property
    def utc(self):
        return float(self._city_info["utc"])

    @utc.setter
    def utc(self, value):
        self._city_info["utc"] = value

    @property
    def city_info(self):
        return self._city_info

    @city_info.setter
    def city_info(self, city_dict):
        self.__update(city_dict)

    def __str__(self):
        """
        Improve print for debug.

        :return:
        """
        __s = (
            "Informations about city : {city}\n"
            "\t- Continent : {continent}\n"
            "\t- Country : {country}\n"
            "\t- Country code : {cc}\n"
            "\t- State : {state}\n"
            "\t- Latitude : {lat}\n"
            "\t- Longitude : {lng}\n"
            "\t- TimeZone : {tz}\n"
            "\t- UTC Offset : {utc}\n".format(
                city=self.city,
                continent=self.continent,
                country=self.country,
                state=self.state,
                lat=self.lat,
                lng=self.lng,
                tz=self.tz,
                utc=self.utc,
                cc=self.cc,
            )
        )
        return __s

    def __update(self, d):
        """
        Update class attributes with new dictionnary.

        :param d:
        :return:
        """
        if not isinstance(d, dict):
            raise TypeError("Argument must be a dictionnary")

        self.city = d["city"]
        self.continent = d["continent"]
        self.country = d["country"]
        self.cc = d["cc"]
        self.state = d["state"]
        self.lat = d["lat"]
        self.lng = d["lng"]
        self.tz = d["tz"]
        self.utc = get_utc_offset(self.tz)
