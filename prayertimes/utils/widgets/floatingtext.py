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

from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSignal, QTimer


class PMXMessageOverlay(object):
    """
    Mixin for displaying overlayed messages in a QWidget instance.
    Please note that you should:
        * Use the mixin on toplevel elements (no QWidgets, but QPlainTextEdit, QWebView, etc.)
        * You should call update_position at least in resizeEvent of your subclass
    """

    def __init__(self):
        self.message_overlay = LabelOverlay(text="", parent=self)

        self.message_overlay.fadedIn.connect(self.message_faded_in)
        self.message_overlay.fadedOut.connect(self.message_faded_out)
        self.message_overlay.messageClicked.connect(self.message_clicked)

        self.active_message = False
        self._time = 2000

    def message_faded_in(self):
        """ Override """
        pass

    def message_clicked(self):
        """ Override """
        pass

    def message_faded_out(self):
        """ Override """
        self.active_message = False
        pass

    def change_timer(self, timer):
        """
        Change timer of popup.
        :param timer:
        :return:
        """
        self._time = timer

    def update_message(self, message):
        self.message_overlay.setText(message)
        self.message_overlay.update_position()
        self.message_overlay.adjustSize()

    def show_message(self, message):
        # Avoid problem when clicking multiple times
        if self.active_message:
            return

        self.update_message(message)

        if message:
            self.active_message = True
            self.message_overlay.fade_in()
        else:
            self.message_overlay.fade_out()

        QTimer(self).singleShot(self._time, self.message_overlay.fade_out)

    def update_message_position(self):
        self.message_overlay.update_position()


class LabelOverlay(QtWidgets.QLabel):
    """
    Inner message QLabel.
    StyleSheet
    Don't use this widget separately, please use PMXMessageOverlay API
    """

    fadedOut = pyqtSignal()
    fadedIn = pyqtSignal()
    messageClicked = pyqtSignal()

    STYLESHEET = """
    QLabel, QLabel link {
        color: rgb(187, 187, 187); /* rgb(187, 187, 187); */
        background-color: rgb(187, 187, 187);
        border: 1px solid;
        border-color: rgb(255, 51, 51);
        border-radius: 0px;
        padding: 4px;
    }
    """

    def __init__(self, text="", parent=None):
        super(LabelOverlay, self).__init__(text, parent)
        self.paddingLeft = 2
        self.paddingBottom = 2
        self.timer_transition = QTimer(self)
        self.timer_transition.setInterval(32)
        self.timer_transition.timeout.connect(self.update_opacity)
        self.speed = 0
        self.setStyleSheet(self.STYLESHEET)
        self.opacity = 0

    def setParent(self, parent, **kwargs):
        self.update_position()
        return super(LabelOverlay, self).setParent(parent)

    def update_position(self):
        if hasattr(self.parent(), 'viewport'):
            parent_rect = self.parent().viewport().rect()
        else:
            parent_rect = self.parent().rect()

        if not parent_rect:
            return

        x = parent_rect.width() - self.width() - self.paddingLeft
        y = parent_rect.height() - self.height() - self.paddingBottom
        self.setGeometry(x, y, self.width(), self.height())

    def resizeEvent(self, event):
        super(LabelOverlay, self).resizeEvent(event)
        self.update_position()

    def showEvent(self, event):
        self.update_position()
        return super(LabelOverlay, self).showEvent(event)

    FULL_THRESHOLD = 0.9
    DEFAULT_FADE_SPEED = 0.15

    def fade_in(self):
        self.opacity = 0
        self.speed = self.DEFAULT_FADE_SPEED
        self.timer_transition.start()

    def fade_out(self):
        self.opacity = self.FULL_THRESHOLD
        self.speed = -self.DEFAULT_FADE_SPEED
        self.timer_transition.start()

    # Text color
    __color = QColor(200, 200, 200)

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        assert isinstance(value, QColor)
        self.__color = value

    __backgroundColor = QColor(22, 31, 38)

    @property
    def background_color(self):
        return self.__backgroundColor

    @background_color.setter
    def background_color(self, value):
        assert isinstance(value, QColor)
        self.__backgroundColor = value
        self._update_stylesheet_alpha()

    # Border color
    __borderColor = QColor(255, 51, 51)

    @property
    def border_color(self):
        return self.__borderColor

    @border_color.setter
    def border_color(self, value):
        assert isinstance(value, QColor)
        self.__borderColor = value
        self._update_stylesheet_alpha()

    __opacity = 1.0

    @property
    def opacity(self):
        return self.__opacity

    @opacity.setter
    def opacity(self, value):
        # assert value <= 1, "{} is not in 0..1 value".format(value)
        if value < 0:
            value = 0
        elif value > 1:
            value = 1
        self.__opacity = value
        self._update_stylesheet_alpha()

    def mousePressEvent(self, event):
        self.messageClicked.emit()

    def update_opacity(self):
        if self.speed > 0:
            if self.isHidden():
                self.show()
            if self.opacity <= self.FULL_THRESHOLD:
                self.opacity += self.speed
            else:
                self.timer_transition.stop()
                self.fadedIn.emit()

        elif self.speed < 0:
            if self.opacity > 0:
                self.opacity += self.speed
            else:
                self.timer_transition.stop()
                self.fadedOut.emit()
                self.hide()

    COLOR_PATTERN = re.compile(r"(?<!-)color:\s*rgba?\([\d,\s%\w]*\);?", re.MULTILINE | re.UNICODE)
    BACKGROUND_COLOR_PATTERN = re.compile(r"background-color:\s*rgba?\([\d,\s%\w]*\);?", re.MULTILINE | re.UNICODE)
    BORDER_COLOR_PATTERN = re.compile(r"border-color:\s*rgba?\([\d,\s%\w]*\);?", re.MULTILINE | re.UNICODE)

    def _update_stylesheet_alpha(self):
        stylesheet = self.styleSheet()
        # re.sub(pattern, repl, string, count, flags)

        for regex, name, col in ((self.COLOR_PATTERN, 'color', self.color),
                                 (self.BACKGROUND_COLOR_PATTERN, 'background-color', self.background_color),
                                 (self.BORDER_COLOR_PATTERN, 'border-color', self.border_color)):
            repl = '%s: rgba(%d, %d, %d, %d%%);' % (name, col.red(), col.green(), col.blue(), self.opacity * 100.0)
            stylesheet = regex.sub(repl, stylesheet)
        self.setStyleSheet(stylesheet)
