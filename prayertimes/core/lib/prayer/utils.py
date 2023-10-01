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

import datetime

from PyQt6.QtCore import QTime


def dt_from_string(s):
    """
    Convert string format time to datetime object.

    :param s: date string object to be converted to datetime object.
    :return:
    """
    qtime = QTime.fromString(s, "HH:mm")
    return datetime.time(qtime.hour(), qtime.minute())


def from_24_to_12(time_format_24):
    """
    Convert string 24h format time to 12h.

    :param time_format_24: time string in 24h format.
    :return:
    """
    qtime = QTime.fromString(time_format_24, "HH:mm")
    return str(qtime.toString("h:mm AP")).strip()


def from_12_to_24(time_format_12):
    """
    Convert string 12h format time to 24h.

    :param time_format_12: time string in 12h format.
    :return:
    """
    qtime = QTime.fromString(time_format_12, "h:mm AP")
    return str(qtime.toString("HH:mm")).strip()


def get_hour_minute(dt):
    """
    Convert full time hh:mm:ss object to hh:mm object.

    :param dt: datetime object to be converted to string object.
    :return:
    """
    qtime = QTime.fromString(str(dt).strip(), "HH:mm:ss")
    return str(qtime.toString("HH:mm")).strip()
