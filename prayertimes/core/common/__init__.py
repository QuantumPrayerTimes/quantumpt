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

import hashlib
import os
import re
import sys
import traceback

from ipaddress import IPv4Address, IPv6Address, AddressValueError

from PyQt6 import QtCore
from PyQt6.QtCore import QCryptographicHash

from prayertimes.core.common.logapi import log


def trace_error_handler(logger):
    """
    Log the calling path of an exception

    :param logger: logger to use so traceback is logged to correct class
    :return:
    """
    log_string = "QuantumPT Error trace"
    for tb in traceback.extract_stack():
        log_string = "{}\n   File {} at line {} \n\t called {}".format(
            log_string, tb[0], tb[1], tb[3]
        )
    logger.error(log_string)


def check_directory_exists(directory, do_not_log=False):
    """
    Check a directory exists and if not create it

    :param directory: The directory to make sure exists
    :param do_not_log: To not log anything. This is need for the start up, when the log isn't ready
    :return:
    """
    if not do_not_log:
        log.debug("check_directory_exists {}".format(directory))
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except IOError:
        if not do_not_log:
            log.exception("failed to check if directory exists or create directory")


def translate(
    context, text, comment=None, qt_translate=QtCore.QCoreApplication.translate
):
    """
    A special shortcut method to wrap around the Qt translation functions.
    This abstracts the translation procedure so that we can change it if at a
    later date if necessary, without having to redo the whole of QuantumPT.

    :param context: The translation context, used to give each string a context or a namespace
    :param text: The text to put into the translation tables for translation
    :param comment: An identifying string for when the same text is used in different roles within the same context
    :param qt_translate:
    :return:
    """
    return qt_translate(context, text, comment)


def de_hump(name):
    """
    Change any Camel Case string to python string

    :param name:
    :return:
    """
    first_camel_case = re.compile("(.)([A-Z][a-z]+)")
    second_camel_case = re.compile("([a-z0-9])([A-Z])")

    sub_name = first_camel_case.sub(r"\1_\2", name)
    return second_camel_case.sub(r"\1_\2", sub_name).lower()


def is_win():
    """
    Returns true if running on a system with a nt kernel e.g. Windows, Wine

    :return: True if system is running a nt kernel false otherwise
    """
    return os.name.startswith("nt")


def is_macosx():
    """
    Returns true if running on a system with a darwin kernel e.g. Mac OS X

    :return: True if system is running a darwin kernel false otherwise
    """
    return sys.platform.startswith("darwin")


def is_linux():
    """
    Returns true if running on a system with a linux kernel e.g. Ubuntu, Debian, etc

    :return: True if system is running a linux kernel false otherwise
    """
    return sys.platform.startswith("linux")


def _validate_ipv4(addr):
    """
    Validate an IPv4 address

    :param addr: Address to validate
    :returns: bool
    """
    try:
        IPv4Address(addr)
        return True
    except AddressValueError:
        return False


def _validate_ipv6(addr):
    """
    Validate an IPv6 address

    :param addr: Address to validate
    :returns: bool
    """
    try:
        IPv6Address(addr)
        return True
    except AddressValueError:
        return False


def verify_ip_address(addr):
    """
    Validate an IP address as either IPv4 or IPv6

    :param addr: Address to validate
    :returns: bool
    """
    return True if _validate_ipv4(addr) else _validate_ipv6(addr)


def md5_hash(salt, data=None):
    """
    Returns the hashed output of md5sum on salt,data
    using Python3 hashlib

    :param salt: Initial salt
    :param data: OPTIONAL Data to hash
    :returns: str
    """
    log.debug('md5_hash(salt="%s")' % salt)
    hash_obj = hashlib.new("md5")
    hash_obj.update(salt)
    if data:
        hash_obj.update(data)
    hash_value = hash_obj.hexdigest()
    log.debug('md5_hash() returning "%s"' % hash_value)
    return hash_value


def qmd5_hash(salt, data=None):
    """
    Returns the hashed output of MD5Sum on salt, data
    using PyQt6.QCryptographicHash

    :param salt: Initial salt
    :param data: OPTIONAL Data to hash
    :returns: str
    """
    log.debug('qmd5_hash(salt="%s"' % salt)
    hash_obj = QCryptographicHash(QCryptographicHash.Md5)
    hash_obj.addData(salt)
    if data:
        hash_obj.addData(data)
    hash_value = hash_obj.result().toHex()
    log.debug('qmd5_hash() returning "%s"' % hash_value)
    return hash_value.data()
