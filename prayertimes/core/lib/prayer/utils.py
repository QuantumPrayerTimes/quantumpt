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

import re
import time
import datetime

from prayertimes.core.common.logapi import log


def dt_from_string(s):
    """
    Convert string format time to datetime object.

    :param s: date string object to be converted to datetime object.
    :return:
    """
    try:
        h, m = [int(s) for s in re.findall(r'\b\d+\b', s)]
    except ValueError:
        log.exception("Cannot convert string format time to datetime object for {}".format(s))
        return
    return datetime.time(h, m)


def from_24_to_12(time_format_24):
    """
    Convert string 24h format time to 12h.

    :param time_format_24: time string in 24h format.
    :return:
    """
    formatted_time = time.strftime("%I:%M %p", time.strptime(str(time_format_24).strip(), "%H:%M"))
    # Remove first number if it is a 0
    if formatted_time[0] == '0':
        formatted_time = formatted_time[1:]
    return str(formatted_time).strip()


def from_12_to_24(time_format_12):
    """
    Convert string 12h format time to 24h.

    :param time_format_12: time string in 12h format.
    :return:
    """
    formatted_time = time.strftime("%H:%M", time.strptime(str(time_format_12).strip(), "%I:%M %p"))
    return str(formatted_time).strip()


def get_hour_minute(dt):
    """
    Convert full time hh:mm:ss object to hh:mm object.

    :param dt: datetime object to be converted to string object.
    :return:
    """
    dt_ = time.strftime("%H:%M", time.strptime(str(dt).strip(), "%H:%M:%S"))
    return dt_
