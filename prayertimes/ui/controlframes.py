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
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPixmap

from prayertimes.core.common import translate
from prayertimes.core.common.logapi import log
from prayertimes.core.common.settings import Settings

from prayertimes.ui.abstract import ControlOption


class ControlVolume(ControlOption):
    def __init__(self, parent=None):
        super(ControlVolume, self).__init__(obj_name=self.__class__.__name__,
                                            icon=":/icons/controloption_volume.png",
                                            parent=parent)

        self.vol_info = QtWidgets.QLabel("{} %".format(self.sld.value()))
        self.vol_info.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.vol_info.setFixedWidth(40)

        self.sld.valueChanged.connect(self._vol_control)
        self.sld.setValue(Settings().value('general_settings/volume'))

        self.layout.addWidget(self.vol_info)

    def showEvent(self, *args, **kwargs):
        self.move(self.parent().volume_tb.x(), self.parent().volume_tb.y() - 60)
        super(ControlVolume, self).showEvent(*args)

    def _vol_control(self):
        """
        Control volume of every player using MediaManager.

        :return:
        """
        if self.sld.value() == 0:
            self.ctrl_icon.setPixmap(QPixmap(":/icons/controloption_volume_none.png"))
        else:
            self.ctrl_icon.setPixmap(QPixmap(":/icons/controloption_volume.png"))
        self.vol_info.setText("{} %".format(self.sld.value()))
        # Control athan, dua, player test and dua controller sound
        self.media_manager.set_volume(self.sld.value())
        Settings().setValue('general_settings/volume', self.sld.value())


class ControlOpacity(ControlOption):
    def __init__(self, parent=None):
        super(ControlOpacity, self).__init__(obj_name=self.__class__.__name__,
                                             icon=":/icons/controloption_opacity.png",
                                             parent=parent)

        self.sld.setRange(0, 100)
        self.sld.setMaximum(30)
        self.sld.valueChanged[int].connect(self._ctrl_opacity)

    def showEvent(self, *args, **kwargs):
        self.move(self.parent().opacity_tb.x(), self.parent().opacity_tb.y() - 60)
        super(ControlOpacity, self).showEvent(*args)

    def _ctrl_opacity(self, value):
        """
        Change opacity of the program.

        :return:
        """
        _opacity = 1 - value / 100
        self.window().setWindowOpacity(_opacity)


class ControlDua(ControlOption):
    def __init__(self, parent=None):
        super(ControlDua, self).__init__(obj_name=self.__class__.__name__,
                                         icon=None,
                                         parent=parent)

        self.layout.removeWidget(self.sld)
        self.layout.removeWidget(self.ctrl_icon)

        self.dua_label = QtWidgets.QLabel(translate('Application', 'Activate dua scheduler (min. interval)'), self)

        self.spinbox_dua_timing = QtWidgets.QSpinBox(self)
        self.spinbox_dua_timing.setRange(1, 90)
        self.spinbox_dua_timing.valueChanged[int].connect(self._control_timing)

        self.activated_cb = QtWidgets.QCheckBox(self)
        self.activated_cb.setChecked(False)
        self.activated_cb.setFixedSize(20, 20)

        self.activated_cb.stateChanged.connect(self._control_dua)

        self.layout.addWidget(self.activated_cb)
        self.layout.addWidget(self.dua_label)
        self.layout.addStretch()
        self.layout.addWidget(self.spinbox_dua_timing)
        self.layout.addWidget(QtWidgets.QLabel('min.', self))

    def showEvent(self, *args, **kwargs):
        self.move(self.parent().dua_tb.x(), self.parent().dua_tb.y() - 60)
        super(ControlDua, self).showEvent(*args)

    def _control_dua(self):
        """
        Control the state of dua by running/stopping scheduler.

        :return:
        """
        if self.activated_cb.isChecked():
            self.scheduler_manager.run_dua_scheduler(self.media_manager.dua_player.play,
                                                     self.spinbox_dua_timing.value())
            log.debug("Scheduler has been started")
        else:
            self.scheduler_manager.stop_dua_scheduler()
            log.debug("Scheduler has been stopped")

    def _control_timing(self, value):
        """
        Handle spinbox behavior to change minutes interval.

        :param value: minute value between duas.
        :return:
        """
        if self.scheduler_manager.scheduler.get_job(job_id="Dua", jobstore='dua'):
            self.scheduler_manager.reschedule_dua(minutes=value)

    # This frame stay visible with control because it needs settings.
    def eventFilter(self, _, event):
        """
        Override to stay visible with control because it needs settings.

        :param _: object that is controlled.
        :param event: event to catch.
        :return:
        """
        if event.type() == QEvent.WindowActivate:
            return True
        elif event.type() == QEvent.WindowDeactivate:
            self.hide()
            return True
        elif event.type() == QEvent.FocusIn:
            return True
        elif event.type() == QEvent.FocusOut:
            return True
        else:
            return super(ControlDua, self).eventFilter(_, event)
