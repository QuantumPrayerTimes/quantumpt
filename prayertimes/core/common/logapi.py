#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from PyQt5.QtCore import QDir

from logging.handlers import RotatingFileHandler

logs_root_dir = QDir().currentPath() + '/logs'
log_file = logs_root_dir + "/program_logs.log"
log = None


def set_logger():
    """
    Define a log file for logging program output.

    :return:
    """
    global log

    log = logging.Logger(level=logging.DEBUG, name='QuantumPT')

    # Configure formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)8s [%(lineno)3s:%(filename)25s] %(message)s')

    # File logging
    if not QDir().exists(logs_root_dir):
        QDir().mkdir(logs_root_dir)
    fh = RotatingFileHandler(filename=log_file, maxBytes=2 * 1024 * 1024, backupCount=5, encoding='utf-8')
    fh.setLevel(logging.DEBUG)

    fh.setFormatter(formatter)
    log.addHandler(fh)

    # Stream logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    log.addHandler(ch)

set_logger()
