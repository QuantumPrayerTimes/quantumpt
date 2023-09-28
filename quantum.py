#!/usr/bin/env -S python
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

import multiprocessing

from prayertimes import main
from prayertimes.core.common import is_win


if __name__ == "__main__":
    # Add support for using multiprocessing from frozen Windows executable (built using PyInstaller),
    # see https://docs.python.org/3/library/multiprocessing.html#multiprocessing.freeze_support
    if is_win():
        multiprocessing.freeze_support()

    main()
