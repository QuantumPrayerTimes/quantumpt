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

from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve


class OpacityAnimation(object):
    """
    This class handles fade in/fade out animation on appearing widget only.
    """

    FULL_THRESHOLD = 0.9
    DEFAULT_FADE_SPEED = 0.10

    fade_out_finished = pyqtSignal()
    fade_in_finished = pyqtSignal()

    def __init__(self, parent):
        try:
            super(OpacityAnimation, self).__init__(parent)
        except TypeError:
            super(OpacityAnimation, self).__init__()

        self.timer_transition = QTimer()
        self.timer_transition.setInterval(32)
        self.timer_transition.timeout.connect(self.update_opacity)

        # Get the caller widget to apply fade effect
        self.widget = vars()["self"]

        self.speed = 0
        self.opacity = 0

    def fade_in(self):
        """
        Start fade in animation.

        :return:
        """
        self.opacity = 0
        self.speed = self.DEFAULT_FADE_SPEED
        self.timer_transition.start()

    def fade_out(self):
        """
        Start fade out animation.

        :return:
        """
        self.opacity = self.FULL_THRESHOLD
        self.speed = -self.DEFAULT_FADE_SPEED
        self.timer_transition.start()

    def fade_out_over(self):
        """
        Function called when fade out animation is over.

        :return:
        """
        pass

    def fade_in_over(self):
        """
        Function called when fade in animation is over.

        :return:
        """
        pass

    @property
    def opacity(self):
        return self.__opacity

    @opacity.setter
    def opacity(self, value):
        if value < 0:
            value = 0
        elif value > 1:
            value = 1
        self.__opacity = value
        self.widget.setWindowOpacity(self.__opacity)

    def update_opacity(self):
        if self.speed > 0:
            if self.widget.isHidden():
                self.widget.show()
            if self.opacity <= self.FULL_THRESHOLD:
                self.opacity += self.speed
            else:
                self.timer_transition.stop()
                self.fade_in_finished.emit()

        elif self.speed < 0:
            if self.opacity > 0:
                self.opacity += self.speed
            else:
                self.timer_transition.stop()
                self.fade_out_finished.emit()
                self.widget.hide()


class FadeAnimation(object):
    """
    This class handles fade in/fade out animation on every widget.
    However it consumes ~2Mb of memory per use.
    """

    def __init__(self, parent, start_value=0.3):
        try:
            super(FadeAnimation, self).__init__(parent)
        except TypeError:
            super(FadeAnimation, self).__init__()

        # Get the caller widget to apply fade effect
        self.widget = vars()["self"]
        self.start_value = start_value

        self.opacityEffect = QtWidgets.QGraphicsOpacityEffect(self)
        self.widget.setGraphicsEffect(self.opacityEffect)
        self.opacityEffect.setOpacity(start_value)

        self.fadeInAnimation = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.fadeInAnimation.setStartValue(start_value)
        self.fadeInAnimation.setEndValue(1.0)
        self.fadeInAnimation.finished.connect(self.on_finished_fadein_animation)

        self.fadeOutAnimation = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.fadeOutAnimation.setStartValue(1.0)
        self.fadeOutAnimation.setEndValue(start_value)
        self.fadeOutAnimation.finished.connect(self.on_finished_fadeout_animation)

    def on_finished_fadein_animation(self):
        """Override"""
        pass

    def on_finished_fadeout_animation(self):
        """Override"""
        pass

    def fade_in(self, duration):
        """
        Function called when fade in animation is over.

        :return:
        """
        if type(duration) != int:
            raise TypeError("duration should be an integer")
        self.fadeInAnimation.setDuration(duration)
        self.fadeInAnimation.start()

    def fade_out(self, duration):
        """
        Function called when fade out animation is over.

        :return:
        """
        self.fadeOutAnimation.setDuration(duration)
        self.fadeOutAnimation.start()


class AlternatePositionAnimation(object):
    """
    This class handles alternate position animation on widgets.
    It permits to move from a position to another and vice versa.
    """

    def __init__(self, parent):
        try:
            super(AlternatePositionAnimation, self).__init__(parent)
        except TypeError:
            super(AlternatePositionAnimation, self).__init__()

        # Get the caller widget to apply fade effect
        self.widget = vars()["self"]

        self.show_animation = QPropertyAnimation(self.widget, b"pos")
        self.hide_animation = QPropertyAnimation(self.widget, b"pos")

        self.show_animation.setDuration(200)
        self.show_animation.setEasingCurve(QEasingCurve.Type.Linear)

        self.hide_animation.setDuration(200)
        self.hide_animation.setEasingCurve(QEasingCurve.Type.Linear)

        self.show_animation.finished.connect(self.show_finished_animation)
        self.hide_animation.finished.connect(self.hide_finished_animation)

    def set_animation_values(self, start, end):
        """
        Set different animation values.

        :param start: position when starting animation.
        :param end: position when finishing animation.
        :return:
        """
        if not start or not end:
            return

        self.show_animation.setStartValue(start)
        self.show_animation.setEndValue(end)

        self.hide_animation.setStartValue(end)
        self.hide_animation.setEndValue(start)

    def start_show(self):
        """
        Start the showing animation.

        :return:
        """
        self.show_animation.start()

    def start_hide(self):
        """
        Start the hiding animation.

        :return:
        """
        self.hide_animation.start()

    def show_finished_animation(self):
        """
        Function called when show animation is over.

        :return:
        """
        pass

    def hide_finished_animation(self):
        """
        Function called when hide animation is over.

        :return:
        """
        pass
