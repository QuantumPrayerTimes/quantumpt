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

from PyQt5 import QtWidgets

from prayertimes.ui.abstract import Dialog


class CriticalExceptionDialog(Dialog):
    """
    About dialog.
    """

    def __init__(self, parent=None):
        super(CriticalExceptionDialog, self).__init__(width=670, height=380,
                                                      obj_name=self.__class__.__name__,
                                                      titlebar_name="Exception", titlebar_icon=None,
                                                      parent=parent)

        self.v_layout = QtWidgets.QVBoxLayout()

        self.dialog_frame.setLayout(self.v_layout)

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setObjectName("TextEditError")
        self.text_edit.setReadOnly(True)

        self.v_layout.addWidget(self.text_edit)
