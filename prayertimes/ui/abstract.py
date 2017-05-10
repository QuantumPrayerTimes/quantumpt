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
from PyQt5.QtCore import Qt, QEvent, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QColor, QFont

from prayertimes.core.common import translate
from prayertimes.core.common.logapi import log
from prayertimes.core.common.registry import Registry
from prayertimes.core.common.registrymixin import RegistryMixin, UniqueRegistryMixin
from prayertimes.core.common.registryproperties import RegistryProperties
from prayertimes.core.common.settings import Settings

from prayertimes.utils.city_infos import City
from prayertimes.utils.date_timezone import lat_lng_to_dms
from prayertimes.utils.widgets.widgetanimation import OpacityAnimation


class AbstractFrame(QtWidgets.QFrame):
    """
    Abstract frame that will be inherited by all frames classes.

    Functions overrided:
        mousePressEvent - mouseMoveEvent - mouseReleaseEvent

    Make it movable.
    """

    def __init__(self, parent=None):
        super(AbstractFrame, self).__init__(parent=parent)

        # Need to be added, if not, moving frame from a button crash
        self.left_click = False
        self.offset = self.pos()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            self.left_click = True

    def mouseMoveEvent(self, event):
        if self.left_click:
            x = event.globalX()
            y = event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.move(x - x_w, y - y_w)

    def mouseReleaseEvent(self, event):
        self.left_click = False


class AbstractDialog(QtWidgets.QDialog):
    """
    Abstract dialog that will be inherited by all dialogs classes.

    Functions overrided:
        mousePressEvent - mouseMoveEvent - mouseReleaseEvent

    Make it movable.
    """

    def __init__(self, parent=None):
        super(AbstractDialog, self).__init__(parent=parent)

        # Need to be added, if not, moving frame from a button crash
        self.left_click = False
        self.offset = self.pos()

        # Make the dialog modal to ONLY its parent (can have athan notification still available)
        self.setWindowModality(Qt.WindowModal)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
            self.left_click = True

    def mouseMoveEvent(self, event):
        if self.left_click:
            x = event.globalX()
            y = event.globalY()
            x_w = self.offset.x()
            y_w = self.offset.y()
            self.move(x - x_w, y - y_w)

    def mouseReleaseEvent(self, event):
        self.left_click = False

    def reject(self):
        Registry().execute("desactivate_overlay")
        Registry().execute("desactivate_global_blur")
        return super(AbstractDialog, self).reject()

    def accept(self):
        Registry().execute("desactivate_overlay")
        Registry().execute("desactivate_global_blur")
        return super(AbstractDialog, self).accept()

    def showEvent(self, event):
        # current_widget = QtWidgets.QApplication.instance().activeWindow()
        Registry().execute("activate_overlay")
        Registry().execute("activate_global_blur")
        # Center the dialog regarding its parent
        self.move(self.global_frame.frameGeometry().topLeft() +
                  self.global_frame.rect().center() - self.rect().center())
        return super(AbstractDialog, self).showEvent(event)


class AbstractGlobalFrame(UniqueRegistryMixin, AbstractFrame):
    """
    Abstract Global Frame.

    @Functions overrided: mousePressEvent - mouseMoveEvent - mouseReleaseEvent
    Make it resizable.
    """

    def __init__(self, width, height, obj_name, parent=None):
        super(AbstractGlobalFrame, self).__init__(parent)

        self.blur_effect = QtWidgets.QGraphicsBlurEffect(self)
        self.blur_effect.setBlurHints(QtWidgets.QGraphicsBlurEffect.PerformanceHint)

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)

        self.setObjectName(obj_name)
        self.setFixedSize(width, height)
        # self.setMinimumSize(width, height)
        # self.setMaximumSize(width + 300, height + 300)

        # Need to be added, if not, moving frame from a button crash
        self.left_click = False
        self.offset = self.pos()

        # Uncomment code to have the ability to resize frame using right click
        self.drag_x = 0
        self.drag_y = 0
        self.current_x = 0
        self.current_y = 0
        self.right_click = False

    def activate_blur(self):
        """
        Activate global blur of the global frame.

        :return:
        """
        self.blur_effect.setBlurRadius(2)
        self.setGraphicsEffect(self.blur_effect)

    def desactivate_blur(self):
        """
        Desactivate global blur of the global frame.

        :return:
        """
        self.blur_effect.setBlurRadius(0)
        self.setGraphicsEffect(self.blur_effect)

    def mousePressEvent(self, event):
        """
        Override method to control right click button. Used to resize windows (Not yet implmented).

        :param event:
        :return:
        """
        if event.button() == Qt.RightButton:
            self.drag_x = event.x()
            self.drag_y = event.y()
            self.current_x = self.width()
            self.current_y = self.height()
            self.right_click = True

        super(AbstractGlobalFrame, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Override method to control right click button. Used to resize windows (Not yet implmented).

        :param event:
        :return:
        """
        if self.right_click:
            x = max(self.minimumWidth(),
                    self.current_x + event.x() - self.drag_x)
            y = max(self.minimumHeight(),
                    self.current_y + event.y() - self.drag_y)
            self.resize(x, y)

        super(AbstractGlobalFrame, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Override method to control right click button. Used to resize windows (Not yet implmented).

        :param event:
        :return:
        """
        self.right_click = False
        super(AbstractGlobalFrame, self).mouseReleaseEvent(event)


class Dialog(RegistryProperties, RegistryMixin, AbstractDialog):
    """
    Abstract Dialog.

    Base class for dialogs.
    """

    def __init__(self, width, height, obj_name, titlebar_name, titlebar_icon, parent=None):
        super(Dialog, self).__init__(parent)

        self.blur_effect = QtWidgets.QGraphicsBlurEffect()
        self.blur_effect.setBlurHints(QtWidgets.QGraphicsBlurEffect.PerformanceHint)

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)

        self.setFixedSize(width, height)

        self.setObjectName(obj_name)

        self.layout = QtWidgets.QVBoxLayout()
        self.titlebar = AbstractTitleBar(self, title=titlebar_name, icon=titlebar_icon)
        self.dialog_frame = QtWidgets.QFrame(self)

        Registry().register_function("activate_dialog_blur", self.activate_blur)
        Registry().register_function("desactivate_dialog_blur", self.desactivate_blur)

        self.setup_ui()

    def activate_blur(self):
        """
        Activate blur on the dialogs.

        :return:
        """
        self.blur_effect.setBlurRadius(2)
        self.setGraphicsEffect(self.blur_effect)

    def desactivate_blur(self):
        """
        Desactivate blur on the dialogs.

        :return:
        """
        self.blur_effect.setBlurRadius(0)
        self.setGraphicsEffect(self.blur_effect)

    def setup_ui(self):
        """
        Setup the UI layout.

        :return:
        """
        # Set margin between frame and borders
        self.layout.setContentsMargins(1, 1, 1, 1)
        # Set margin between elements of layout
        self.layout.setSpacing(0)

        self.layout.insertWidget(0, self.titlebar)
        self.layout.insertWidget(1, self.dialog_frame)

        self.setLayout(self.layout)


class AbstractTitleBar(QtWidgets.QFrame):
    """
    Abstract TitleBar.

    Used in dialogs.
    """

    def __init__(self, parent=None, title="Dafault", icon=None):
        super(AbstractTitleBar, self).__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setObjectName('TitleBar')

        self.setAutoFillBackground(True)
        self.setFixedHeight(35)

        self.close_button = QtWidgets.QToolButton(self)
        self.close_button.setFixedSize(35, 35)
        self.close_button.setObjectName("close_button")

        self.titlebar_text = QtWidgets.QLabel(title, self)
        self.titlebar_icon = QtWidgets.QLabel(self)
        self.titlebar_icon.setPixmap(QPixmap(icon))

        self.horizontal_layout = QtWidgets.QHBoxLayout(self)

        self.horizontal_layout.insertWidget(0, self.titlebar_text)
        self.horizontal_layout.insertWidget(1, self.titlebar_icon)
        self.horizontal_layout.insertStretch(2)

        self.horizontal_layout.insertWidget(-1, self.close_button)

        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setSpacing(0)

        self.close_button.clicked.connect(self.window().close)


class GlobalTitlebar(AbstractTitleBar):
    """
    The program titlebar inherits to add minimize button and main frame selector hide/show button.
    """

    def __init__(self, parent=None, title="Default", icon=None):
        super(GlobalTitlebar, self).__init__(parent, title, icon)

        self.menu_btn = QtWidgets.QToolButton()
        self.menu_btn.setFixedSize(35, 35)
        self.menu_btn.setObjectName("menu_btn")

        self.min_btn = QtWidgets.QToolButton()
        self.min_btn.setFixedSize(35, 35)
        self.min_btn.setObjectName("min_btn")

        self.horizontal_layout.insertWidget(3, self.min_btn)
        self.horizontal_layout.insertWidget(4, self.menu_btn)

        self.close_button.disconnect()
        self.close_button.clicked.connect(self.close_option)
        self.min_btn.clicked.connect(self.window().showMinimized)

        self.menu_btn.clicked.connect(self._animate_main_frame_selector)
        self.a = False

    def _animate_main_frame_selector(self):
        """
        Animate main frame selector with position animation.

        :return:
        """
        if self.a:
            Registry().execute('expand_main_frame_selector')
        else:
            Registry().execute('hide_main_frame_selector')
        self.a = not self.a

    @staticmethod
    def close_option():
        """
        Handles the closing from application titlebar (close button).

        :return:
        """
        if Settings().value("general_settings/close") == 0:
            Registry().execute("hide_app_in_systray")
        elif Settings().value("general_settings/close") == 1:
            Registry().execute("close_application")
        else:
            log.warning("Not defined, by default, use hide in system tray")
            Registry().execute("hide_app_in_systray")


class ControlOption(UniqueRegistryMixin, RegistryProperties, QtWidgets.QFrame):
    """
    Control frame that is generic to adapt.

    Used in VolumeControl, DuaControl and OpacityControl.
    """
    def __init__(self, obj_name, icon=None, parent=None):
        super(ControlOption, self).__init__(parent)

        self.setObjectName(obj_name)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self.layout = QtWidgets.QHBoxLayout(self)
        # self.layout.setContentsMargins(0, 0, 0, 0)
        # self.layout.setSpacing(0)

        self.ctrl_icon = QtWidgets.QLabel()
        self.ctrl_icon.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.ctrl_icon.setPixmap(QPixmap(icon))

        self.sld = QtWidgets.QSlider(Qt.Horizontal)
        self.sld.setFocusPolicy(Qt.NoFocus)
        self.sld.setRange(0, 100)

        self.resize(310, 50)

        self.layout.addWidget(self.ctrl_icon)
        self.layout.addWidget(self.sld)

        self.installEventFilter(self)

    def eventFilter(self, _, event):
        """
        Filter the events that happen when clicking inside/outside the frame.

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
            self.hide()
            return True
        else:
            return super(ControlOption, self).eventFilter(_, event)


class ColorFrame(QtWidgets.QFrame):
    """
    Simple color frame.
    """

    def __init__(self, width, height, color, parent=None):
        super(ColorFrame, self).__init__(parent)
        self.setFixedSize(width, height)
        self.setObjectName(self.__class__.__name__)
        self._color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        self.setStyleSheet(
            """
            background-color: rgba({r}, {g}, {b}, {a});
            """.format(r=self.color.red(),
                       g=self.color.green(),
                       b=self.color.blue(),
                       a=self.color.alpha())
        )


class ConstructionFrame(QtWidgets.QFrame):
    """
    Contruction frame used to display a simple message.
    """
    def __init__(self, text="", parent=None):
        super(ConstructionFrame, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel(text, self)
        self.label.setStyleSheet(
            """
            background-color: transparent;
            color: #ff3333;
            font: 13px Ubuntu;
            font-weight: bold;
            """
        )

        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)


class ListView(QtWidgets.QListView):
    """
    ListView used to display cities in different countries.
    Much faster and cleaner than QListWidget.
    """
    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        # Layout items in batches instead of waiting for all items to be
        # loaded before user is allowed to interact with them.
        self.setLayoutMode(QtWidgets.QListView.Batched)
        self.setUniformItemSizes(True)
        # Read only cells
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # Remove the blank area at the end of the ListView
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)


class ListWidgetSelectorFrame(QtWidgets.QListWidget):
    """
    Class used to select widgets as list and select different frames.

    MainFrameSelector and SettingsFrameSelector use this class.
    """

    def __init__(self, parent=None):
        super(ListWidgetSelectorFrame, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setUniformItemSizes(True)


class SideLabel(QtWidgets.QFrame):
    """
    Label inside a ListWidgetSelectorFrame class.

    It can display arabic or english message with given orientation.
    """
    selected = pyqtSignal()
    unselected = pyqtSignal()

    def __init__(self, parent=None, label=None, icon=None,
                 w_colorframe=0, h_colorframe=0, alignment='left', color=QColor(255, 165, 0)):
        super(SideLabel, self).__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setObjectName(self.__class__.__name__)
        self.setMouseTracking(True)

        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.horizontal_layout.setSpacing(10)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)

        self.color = color

        self.color_frame = ColorFrame(width=w_colorframe, height=h_colorframe,
                                      color=self.color, parent=self)

        self.label_setting = QtWidgets.QLabel(label, self)

        # self.label_icon = QtWidgets.QLabel(self)
        # self.label_icon.setPixmap(QPixmap(icon))

        if alignment == 'right':
            self.horizontal_layout.setDirection(QtWidgets.QBoxLayout.RightToLeft)
            self.label_setting.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        elif alignment == 'left':
            self.horizontal_layout.setDirection(QtWidgets.QBoxLayout.LeftToRight)
            self.label_setting.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.horizontal_layout.addWidget(self.color_frame)
        # self.horizontal_layout.addWidget(self.label_icon)
        self.horizontal_layout.addWidget(self.label_setting)

        self.selected.connect(self._selected)
        self.unselected.connect(self._unselected)

    def _selected(self):
        self.color_frame.color = self.color
        self.label_setting.setStyleSheet(
            """
            color: rgb({r}, {g}, {b});
            """.format(r=self.color.red(),
                       g=self.color.green(),
                       b=self.color.blue())
        )

    def _unselected(self):
        self.color_frame.color = QColor(0, 0, 0, 0)
        self.label_setting.setStyleSheet(
            """
            background-color: transparent;
            color: rgb(187, 187, 187);
            """
        )


class TaskThread(QThread):

    def __init__(self, _function, *args, **kwargs):
        super(TaskThread, self).__init__()
        self.return_value = None

        self.function = _function
        self.args = args
        self.kwargs = kwargs

        self.finished.connect(self.on_finished)

    def run(self, *args):
        self.return_value = self.function(*self.args, **self.kwargs)

    def on_finished(self):
        """ Override """
        pass

    def exit(self, return_code=0):
        """ Override """
        return super(TaskThread, self).exit(returnCode=return_code)

    def stop(self, exit_code):
        """ Override """
        self.exit(exit_code)

    def quit(self):
        """ Override """
        return super(TaskThread, self).quit()


class FrameCitySetting(QtWidgets.QFrame):

    def __init__(self, parent=None, with_map=False):
        super(FrameCitySetting, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        if with_map:
            self._map_image = QtWidgets.QLabel(self)
            self._map_image.setPixmap(QPixmap(':/icons/framecity_map.png'))

        self._continent = QtWidgets.QLabel(self)
        self._state = QtWidgets.QLabel(self)
        self._country = QtWidgets.QLabel(self)
        self._city = QtWidgets.QLabel(self)
        self._coordinates = QtWidgets.QLabel(self)
        self._coordinates_formatted = QtWidgets.QLabel(self)
        self._tz = QtWidgets.QLabel(self)

        self.location_label = QtWidgets.QLabel(translate('Application', 'Location'), self)
        self.location_label.setStyleSheet("QLabel {font: 30px 'capsuula'; color: #204550}")

        self.cooridnates_label = QtWidgets.QLabel(translate('Application', 'Coordinates'), self)
        self.cooridnates_label.setStyleSheet("QLabel {font: 30px 'capsuula'; color: #204550}")

        self.tz_label = QtWidgets.QLabel(translate('Application', 'Timezone'), self)
        self.tz_label.setStyleSheet("QLabel {font: 30px 'capsuula'; color: #204550}")

        self.h_layout = QtWidgets.QHBoxLayout(self)

        self.v_left_layout = QtWidgets.QVBoxLayout()
        self.v_right_layout = QtWidgets.QVBoxLayout()

        self.v_left_layout.addWidget(self.location_label)
        self.v_left_layout.addWidget(self._continent)
        self.v_left_layout.addWidget(self._country)
        self.v_left_layout.addWidget(self._state)
        self.v_left_layout.addWidget(self._city)
        self.v_left_layout.addStretch()

        self.v_right_layout.addWidget(self.cooridnates_label)
        self.v_right_layout.addWidget(self._coordinates)
        self.v_right_layout.addWidget(self._coordinates_formatted)
        self.v_right_layout.addStretch()
        self.v_right_layout.addWidget(self.tz_label)
        self.v_right_layout.addWidget(self._tz)

        self.h_layout.addLayout(self.v_left_layout)
        self.h_layout.addLayout(self.v_right_layout)

        if with_map:
            self.h_layout.addWidget(self._map_image)

    def update_labels(self, city_object):
        """
        Update label of frame from a City object.

        :param city_object:
        :return:
        """
        assert isinstance(city_object, City)

        self._continent.setText("{0} : {1:}".format('Continent', city_object.continent))
        self._country.setText("{0} : {1:}".format('Country', city_object.country))
        self._state.setText("{0} : {1:}".format('State', city_object.state))
        self._city.setText("{0} : {1:}".format('City', city_object.city))
        self._coordinates.setText('Coordinates : {} | {}'.format(city_object.lat, city_object.lng))
        self._coordinates_formatted.setText('Coordinates : {}'.format(lat_lng_to_dms(float(city_object.lat),
                                                                                     float(city_object.lng))))
        self._tz.setText('Timezone - UTC : {} | {}'.format(city_object.tz, city_object.utc))

    def clear(self):
        """
        Clear labels of frame.

        :return:
        """

        self._continent.clear()
        self._country.clear()
        self._state.clear()
        self._city.clear()
        self._coordinates.clear()
        self._coordinates_formatted.clear()
        self._tz.clear()


class CheckableButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(CheckableButton, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setCheckable(True)


class NotificationFrame(RegistryProperties, OpacityAnimation, QtWidgets.QDialog):
    """
    General notification frame that appears on top of current widget and prevent
    the use of the general application except athan frame that appears to give
    the ability to stop athan.

    Need to call this NotificationFrame with a parent to stop interaction with all
    widgets inside this parent, grand parent, childs etc ...

    If no parent is specified, GlobalFrame will be taken as parent and the whole
    application cannot be used while NotificationFrame is visible.
    """

    OK = 0
    WARNING = 1
    ERROR = 2

    map_type = {OK: ['Good', ':/icons/notification_ok.png'],
                WARNING: ['Warning !', ':/icons/notification_warning.png'],
                ERROR: ['Error !', ':/icons/notification_error.png']}

    def __init__(self, parent=None):
        super(NotificationFrame, self).__init__(parent)

        # Take the GlobalFrame as parent if no parent is specified.
        if not parent:
            self.setParent(self.global_frame)

        self.setMaximumWidth(600)

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)

        # Make the dialog modal to ONLY its parent (to have athan notification still available)
        # Need to call the Notification frame with self : e.g NotificationFrame(self)
        self.setWindowModality(Qt.WindowModal)
        self.setModal(True)

        self.setObjectName(self.__class__.__name__)

        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.setSpacing(10)

        self.message = QtWidgets.QLabel('', self)
        font = QFont("ubuntu", 10)
        self.message.setFont(font)

        self.title = QtWidgets.QLabel('', self)
        font = QFont("capsuula", 20)
        self.title.setFont(font)

        self.icon = QtWidgets.QLabel(self)

        self.close_button = QtWidgets.QPushButton('OK', self)
        self.close_button.clicked.connect(self.fade_out)

        # self.main_layout.addWidget(self.close_bt, 0, 0)
        self.main_layout.addWidget(self.icon, 1, 0, 2, 2)
        self.main_layout.addWidget(self.title, 1, 2, 1, 4)
        self.main_layout.addWidget(self.message, 2, 2, 1, 4)
        self.main_layout.addWidget(self.close_button, 3, 5, 1, 1)

        self.fade_in_finished.connect(self.fade_in_over)
        self.fade_out_finished.connect(self.fade_out_over)

        self.setLayout(self.main_layout)

    def notify(self, msg_type, msg, title='', button_text="OK"):
        self.message.setText(msg)
        self.icon.setPixmap(QPixmap(self.map_type[msg_type][1]))
        if not title:
            self.title.setText(self.map_type[msg_type][0])
        else:
            self.title.setText(title)
        self.close_button.setText(button_text)
        self.show()

    def showEvent(self, event):
        # active_widget = QtWidgets.QApplication.instance().activeWindow()
        # if active_widget.metaObject().className() == 'GlobalFrame':
        #     Registry().execute("activate_overlay")
        #     Registry().execute("activate_global_blur")
        # else:
        #     Registry().execute("activate_dialog_blur")
        # Registry().execute("activate_overlay")
        # Registry().execute("activate_global_blur")

        # Raise window if minimized or in SysTray
        if self.global_frame.isHidden():
            self.global_frame.show()
        if self.global_frame.windowState() & Qt.WindowMinimized:
            self.global_frame.setWindowState(Qt.WindowActive)
        if self.global_frame.isVisible():
            self.global_frame.window().activateWindow()

        # Center the notification frame regarding its parent
        self.move(self.global_frame.frameGeometry().topLeft() +
                  self.global_frame.rect().center() - self.rect().center())
        self.fade_in()
        return super(NotificationFrame, self).showEvent(event)

    def fade_in(self):
        """
        Begin the animation of Notification frame.

        :return:
        """
        return super(NotificationFrame, self).fade_in()

    def reject(self):
        """
        Dialog has been closed either close button or accepted.

        :return:
        """
        self.fade_out()

    def fade_out_over(self):
        """
        Function called when fade out animation is over.

        :return:
        """
        # active_widget = QtWidgets.QApplication.instance().activeWindow()
        # if active_widget.metaObject().className() == 'GlobalFrame':
        #     Registry().execute("desactivate_overlay")
        #     Registry().execute("desactivate_global_blur")
        # else:
        #     Registry().execute("desactivate_dialog_blur")
        # Registry().execute("desactivate_overlay")
        # Registry().execute("desactivate_global_blur")
        pass


class WelcomeNotification(NotificationFrame):

    def __init__(self, parent=None):
        super(WelcomeNotification, self).__init__(parent)

        self.setObjectName(self.__class__.__bases__[0].__name__)

    def showEvent(self, event):
        Registry().execute("activate_overlay")
        Registry().execute("activate_global_blur")
        return super(WelcomeNotification, self).showEvent(event)

    def fade_out_over(self):
        Registry().execute("desactivate_overlay")
        Registry().execute("desactivate_global_blur")
        return super(WelcomeNotification, self).fade_out_over()
