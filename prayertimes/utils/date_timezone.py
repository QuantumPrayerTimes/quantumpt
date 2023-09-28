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

import pytz
import datetime
import time

today = datetime.datetime.today()


def is_dst(timezone, date=today):
    """
    Determine if it's Daylight Saving Time from a date and a Timezone.

    :param timezone:
    :param date:
    :return:
    """
    pst_ = pytz.timezone(timezone)
    if date:
        return bool(pst_.localize(date).dst())
    else:
        return bool(datetime.datetime.now(pst_).dst())


def get_utc_offset(timezone, date=today):
    """
    Get the UTC offset (including DST if available) from a date and a Timezone.

    :param timezone:
    :param date:
    :return:
    """
    if not isinstance(timezone, str):
        raise Exception("Please prodive a valid TimeZone")
    pst_ = pytz.timezone(timezone)
    utc_offset = pst_.utcoffset(date).total_seconds() / 3600
    return utc_offset


def get_utc_offset_str():
    """
    Returns a UTC offset string of the current time suitable for use in the
    most widely used timestamps (i.e. ISO 8601, RFC 3339).

    For example:
    10 hours ahead, 5 hours behind, and time is UTC: +10:00, -05:00, +00:00

    Works only locally.
    """

    # Calculate the UTC time difference in seconds.
    timestamp = time.time()
    time_now = datetime.datetime.fromtimestamp(timestamp)
    time_utc = datetime.datetime.utcfromtimestamp(timestamp)
    utc_offset_secs = (time_now - time_utc).total_seconds()

    # If the current time is behind UTC convert the offset
    # seconds to a positive value and set the flag variable.
    if utc_offset_secs < 0:
        utc_offset_secs *= -1
        pos_neg_prefix = "-"
    else:
        pos_neg_prefix = "+"

    utc_offset = time.gmtime(utc_offset_secs)
    utc_offset_fmt = time.strftime("%H:%M", utc_offset)
    utc_offset_str = pos_neg_prefix + utc_offset_fmt

    return utc_offset_str


def decimal_to_dms(value, value_type):
    """
    Converts a Decimal Degree Value into Degrees Minute Seconds Notation.

    :param value:
    :param value_type: type of the value passed, 'Longitude' or 'Latitude'
    :return:
    """
    is_positive = value >= 0
    dd = abs(value)
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees

    direction = ""
    if value_type == "Longitude":
        if degrees < 0:
            direction = "W"
        elif degrees > 0:
            direction = "E"
        else:
            direction = ""
    elif value_type == "Latitude":
        if degrees < 0:
            direction = "S"
        elif degrees > 0:
            direction = "N"
        else:
            direction = ""
    notation = "{}°{}'{}\"{}".format(
        int(degrees), int(minutes), str(seconds)[0:5], direction
    )
    return notation


def lat_lng_to_dms(latitude, longitude):
    """
    Return a formatted string : e.g : 47°36'55.44"N | -122°12'37.08"W

    :param latitude:
    :param longitude:
    :return:
    """
    lat = decimal_to_dms(latitude, "Latitude")
    lng = decimal_to_dms(longitude, "Longitude")
    return "{} | {}".format(lat, lng)
