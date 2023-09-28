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
from collections import OrderedDict

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap

# from prayertimes.core.common import translate
from prayertimes.core.common.logapi import log
from prayertimes.core.common.registrymixin import UniqueRegistryMixin, RegistryMixin
from prayertimes.core.common.settings import Settings


class AbstractSpinBox(QtWidgets.QSpinBox):
    value_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super(AbstractSpinBox, self).__init__(parent)

        self.valueChanged.connect(
            self.on_value_changed, type=Qt.ConnectionType.QueuedConnection
        )

    def on_value_changed(self):
        self.lineEdit().deselect()
        self.lineEdit().clearFocus()
        # Set the LineEdit of the spinbox unclickable and not modifiable.
        # self.lineEdit().setDisabled(True)
        # self.lineEdit().setReadOnly(True)


class PrayerTimeFrame(RegistryMixin, QtWidgets.QFrame):
    highlight_prayer = pyqtSignal(bool)

    def __init__(
        self, parent=None, prayer_name="Default", prayer_time="12:00", icon=None
    ):
        super(PrayerTimeFrame, self).__init__(parent)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setObjectName(self.__class__.__name__)

        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.setContentsMargins(3, 3, 3, 3)
        self.main_layout.setSpacing(5)

        self.activated_cb = QtWidgets.QCheckBox()
        self.activated_cb.setObjectName("ActivatedPT_TB")
        self.activated_cb.setFixedSize(20, 20)
        self.activated_cb.setChecked(True)

        self.prayer_label = QtWidgets.QLabel(prayer_name)
        self.prayer_label.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.prayer_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter
        )

        self.prayer_time = QtWidgets.QLabel(prayer_time)
        self.prayer_time.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.prayer_time.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter
        )

        self.prayer_icon = QtWidgets.QLabel()
        self.prayer_icon.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )
        self.prayer_icon.setPixmap(QPixmap(icon))

        self.mute_cb = QtWidgets.QCheckBox()
        self.mute_cb.setObjectName("MutePT_TB")
        self.mute_cb.setFixedSize(20, 20)
        self.mute_cb.hide()

        self.adjust_pt = AbstractSpinBox()
        # self.adjust_pt.setRange(-30, 30)
        self.adjust_pt.setRange(-500, 500)  # For debug purpose

        # Property needed to have a dynamic interface with the frame
        self._current = False
        self._time = prayer_time
        self._icon = icon
        self._label = prayer_name

        self.main_layout.addWidget(self.activated_cb, 0, 0, 1, 1)
        self.main_layout.addWidget(self.mute_cb, 0, 5, 1, 1)

        self.main_layout.addWidget(self.prayer_label, 1, 0, 1, 4)
        self.main_layout.addWidget(self.prayer_time, 2, 0, 1, 4)
        self.main_layout.addWidget(self.prayer_icon, 1, 4, 2, 2)

        self.main_layout.addWidget(self.adjust_pt, 5, 0, 1, 6)

        self.setLayout(self.main_layout)

        self.highlight_prayer[bool].connect(self._set_highlight)

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        if value:
            self.highlight_prayer.emit(True)
        else:
            self.highlight_prayer.emit(False)
        self._current = value

    @property
    def time(self):
        return str(self.prayer_time.text()).strip()

    @time.setter
    def time(self, value):
        self.prayer_time.setText(value)

    @property
    def icon(self):
        return self.prayer_icon.pixmap()

    @icon.setter
    def icon(self, value):
        self.prayer_icon.setPixmap(QPixmap(value))

    @property
    def label(self):
        return str(self.prayer_label.text()).strip()

    @label.setter
    def label(self, value):
        self.prayer_label.setText(value)

    @property
    def offset(self):
        return self.adjust_pt.value()

    @offset.setter
    def offset(self, value):
        self.adjust_pt.setValue(value)

    def _set_highlight(self, current=False):
        """
        current = 3 : current_prayer = True  / joumoua = True
        current = 2 : current_prayer = False / joumoua = True
        current = 1 : current_prayer = True  / joumoua = False
        current = 0 : current_prayer = False / joumoua = False

        :param current: new current prayer.
        :return:
        """
        if self.label in ("الظهر", "Dhuhr", "الجمعة") and (
            "Friday" in datetime.datetime.now().strftime("%A")
        ):
            if current:
                self.setProperty("current", 3)
            else:
                self.setProperty("current", 2)
            self.label = "الجمعة"
        else:
            if current:
                self.setProperty("current", 1)
            else:
                self.setProperty("current", 0)

        self.style().unpolish(self)
        self.style().polish(self)


class PrayersContainerFrame(UniqueRegistryMixin, QtWidgets.QFrame):
    """
    PrayersContainerFrame that contains all PrayerTimeFrame.

    PrayersContainerFrame.praytimes :

        Fajr      |   PrayerTimeFrame(prayer_name=label, icon=icon)
        Shourouq  |   PrayerTimeFrame(prayer_name=label, icon=icon)
        Dhuhr     |   PrayerTimeFrame(prayer_name=label, icon=icon)
        Asr       |   PrayerTimeFrame(prayer_name=label, icon=icon)
        Maghrib   |   PrayerTimeFrame(prayer_name=label, icon=icon)
        Isha      |   PrayerTimeFrame(prayer_name=label, icon=icon)

    PrayerTimeFrame
      ____________________________
     | |X|                     |M||
     | prayer_name  **************|
     |              * prayer_icon |
     | prayer_time  **************|
     | ******** offset ********** |
     |____________________________|

    """

    prayer_list = [
        ("Fajr", "الفجر"),
        ("Shourouq", "الشروق"),
        ("Dhuhr", "الظهر"),
        ("Asr", "العصر"),
        ("Maghrib", "المغرب"),
        ("Isha", "العشاء"),
    ]

    icon_set = [
        ":/icons/prayerframe_fajr.png",
        ":/icons/prayerframe_sunrise.png",
        ":/icons/prayerframe_dhuhr.png",
        ":/icons/prayerframe_asr.png",
        ":/icons/prayerframe_sunset.png",
        ":/icons/prayerframe_isha.png",
    ]

    def __init__(self, parent=None):
        super(PrayersContainerFrame, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.layout = QtWidgets.QHBoxLayout(self)

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.prayer_icon = OrderedDict()
        self.praytimes = OrderedDict()

        for p_name in reversed(self.prayer_list):
            # p_name[0] : English
            # p_name[1] : Arabic
            if Settings().contains("general_settings/arabic_names"):
                if Settings().value("general_settings/arabic_names") == 1:
                    self.praytimes[p_name[0]] = PrayerTimeFrame(prayer_name=p_name[1])
                else:
                    self.praytimes[p_name[0]] = PrayerTimeFrame(prayer_name=p_name[0])
            else:
                self.praytimes[p_name[0]] = PrayerTimeFrame(prayer_name=p_name[0])

            # Hide not needed widgets for Shourouq without changing layout form.
            if p_name[0] == "Shourouq":
                for widget in [
                    self.praytimes[p_name[0]].activated_cb,
                    self.praytimes[p_name[0]].mute_cb,
                ]:
                    sp_retain = widget.sizePolicy()
                    sp_retain.setRetainSizeWhenHidden(True)
                    widget.setSizePolicy(sp_retain)
                    widget.hide()

            self.layout.addWidget(self.praytimes[p_name[0]])

    def __application_init__(self):
        self.set_icons(self.icon_set)

    def _update_prayer_name(self, arabic=False):
        """
        Update prayer names language.

        :return:
        """
        for p_name in reversed(self.prayer_list):
            # p_name[0] : English prayer name
            # p_name[1] : Arabic prayer name
            if (
                "Friday" in datetime.datetime.now().strftime("%A")
                and p_name[0] == "Dhuhr"
            ):
                if arabic:
                    self.praytimes[p_name[0]].label = "الجمعة"
                else:
                    self.praytimes[p_name[0]].label = "Joumoua"
                continue
            if arabic:
                self.praytimes[p_name[0]].label = p_name[1]
            else:
                self.praytimes[p_name[0]].label = p_name[0]

    def update_prayer_name(self):
        """
        Update prayer names language according to settings.

        :return:
        """
        if Settings().contains("general_settings/arabic_names"):
            if Settings().value("general_settings/arabic_names") == 0:
                self._update_prayer_name(arabic=False)
            elif Settings().value("general_settings/arabic_names") == 1:
                self._update_prayer_name(arabic=True)
            else:
                log.debug(
                    "value for arabic_names in "
                    "settings.ini: {}".format(
                        Settings().value("general_settings/arabic_names")
                    )
                )
        else:
            self._update_prayer_name(arabic=True)
            Settings().setValue("general_settings/arabic_names", 1)

    def set_icons(self, icon_set):
        """
        Associate icon_set to prayer list and update icons. (Not used for the moment)

        :param icon_set:
        :return:
        """
        self.prayer_icon = OrderedDict(zip(self.prayer_list, icon_set))
        for p_name, icon in self.prayer_icon.items():
            self.praytimes[p_name[0]].icon = QPixmap(icon)

    def set_default_times(self):
        """
        Set the default times to all prayer frames.

        :return:
        """
        for pt_frame in self.praytimes.values():
            pt_frame.time = "12:00"

    def reset_offsets(self):
        """
        Reset the offsets to 0.

        :return:
        """
        for pt_frame in self.praytimes.values():
            pt_frame.offset = 0

    def set_offset(self, prayer, value):
        """
        Set a precise offset <value> to <prayer>

        :param prayer: prayer that needs offset.
        :param value: offset value.
        :return:
        """
        self.praytimes[prayer].offset = value

    def set_current_prayer(self, prayer):
        """
        Set the current prayer to the correct prayer frame.

        :param prayer: current prayer that needs to be set.
        :return:
        """
        for p_name in self.prayer_list:
            if p_name[0] == prayer:
                self.praytimes[p_name[0]].current = True
            else:
                self.praytimes[p_name[0]].current = False

    def toggle_state_athan(self, activate):
        """
        Toggle state of athans from running/stopping mode.

        :param activate: boolean that determine the state.
        :return:
        """
        for p_name in self.prayer_list:
            if p_name[0] == "Shourouq":
                continue
            else:
                self.praytimes[p_name[0]].activated_cb.setChecked(
                    True
                ) if activate else self.praytimes[p_name[0]].activated_cb.setChecked(
                    False
                )
