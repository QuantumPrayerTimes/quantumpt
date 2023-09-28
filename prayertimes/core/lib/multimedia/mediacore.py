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

from enum import Enum

from random import choice

from PyQt6.QtCore import QUrl, QDir
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer


from prayertimes.core.common.logapi import log
from prayertimes.core.common.registry import Registry
from prayertimes.core.common.registryproperties import RegistryProperties
from prayertimes.core.common.resourceslocation import ResourcesLocation
from prayertimes.core.common.settings import Settings


class PlayerPriority(Enum):
    """
    List each player priority.

    Should not need Athan and Dua after athan priority because cannot run on the same time
    due to implementation of AthanMediaPlayer. Dua after atahn is run just after athan
    (if selected).

    The higheset priority means the players will interrupt the player with lower priority.
    """

    ATHAN = 4
    DUA_AFTER_ATHAN = 3
    DUA = 2
    PREVIEW_ATHAN = 1


class MediaPriorityHandler(object):
    """
    Handles priority of players during play function.

    Before play function is executed, check if there is a current player running.

    Algorithmic view:

    FOREACH(player):
        IF <player> is playing
            IF new_player == player
                NEXT(player)
            IF priority(<new_player>) > priority(<player>)
                stop(<player>)
                play(<new_player>)
            ELSE
                nothing (leave current player active)
        ELSE
            NEXT(player)

    """

    __instance__ = None
    __priority__ = {}

    def __new__(cls):
        """
        Re-implement method __new__ to have a singleton.
        """
        if not cls.__instance__:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__

    def __init__(self):
        """
        Initialize all sub classes players and their priority.
        """
        self.__priority__[vars()["self"]] = vars()["self"].priority
        log.debug(
            "media player available : {}".format(vars()["self"].__class__.__name__)
        )

    def prioritize(self, __player):
        for player, priority in self.__priority__.items():
            if player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                if __player == player:
                    log.debug(
                        "media priority: new player same as previous player <{}, {}>".format(
                            player.type.name, player.priority
                        )
                    )
                    continue
                log.debug(
                    "media priority: current player playing <{}, {}>".format(
                        player.type.name, player.priority
                    )
                )
                log.debug(
                    "media priority: new player priority <{}, {}>".format(
                        __player.type.name, __player.priority
                    )
                )
                if __player.priority > priority:
                    player.stop()
                    return True
                else:
                    return False
            else:
                continue

        log.debug(
            "media priority: new player <{}, {}>".format(
                __player.type.name, __player.priority
            )
        )
        return True


class MediaCore(QMediaPlayer, MediaPriorityHandler):
    """
    This is the base class for media players.
    """

    # All paths of medias are declared here
    _dua_after_athan = ResourcesLocation().dua_dir + "/dua_after_athan.mp3"

    list_athans_files = QDir(ResourcesLocation().athan_dir).entryList(["*.mp3"])
    list_athans = list(
        map(QDir(ResourcesLocation().athan_dir).filePath, list_athans_files)
    )

    list_douas_files = QDir(ResourcesLocation().dua_dir).entryList(["*.mp3"])
    list_douas = list(map(QDir(ResourcesLocation().dua_dir).filePath, list_douas_files))

    default_athan = list_athans[0]

    def __init__(self):
        """
        Initialize a Base Player Music object.
        Configured to play music files only.
        """
        super(MediaCore, self).__init__()
        # Must initialize the MediaCore with a media, it is not important
        # which one because it will be set before each play function.
        self.setup_media(self.default_athan)
        self.audio_output = QAudioOutput()
        self.setAudioOutput(self.audio_output)
        self.mediaStatusChanged.connect(self.media_status_changed)

    def setup_volume(self, volume):
        """
        Setup the media that will be played.
        :param media:
        :return:
        """
        self.audio_output.setVolume(float(volume / 100))

    def setup_media(self, media=None):
        """
        Setup the media that will be played.
        :param media:
        :return:
        """
        self.setSource(QUrl.fromLocalFile(media))

    def play(self):
        """
        Common play method, all different players go throught this function before playing.
        Handles prioirity between players.

        :return:
        """
        if self.prioritize(self):
            return super(MediaCore, self).play()
        else:
            pass

    def stop(self):
        """Override"""
        return super(MediaCore, self).stop()

    def media_status_changed(self, status):
        """Override"""
        pass

    def is_playing(self):
        """
        Return player playing status.

        :return:
        """
        return (
            True
            if self.playbackState() == QMediaPlayer.PlaybackState.PlayingState
            else False
        )

    def is_stopped(self):
        """
        Return player stopped status.

        :return:
        """
        return (
            True
            if self.playbackState() == QMediaPlayer.PlaybackState.StoppedState
            else False
        )


class RandomMediaPlayer(MediaCore):
    """
    This is a random media player used for duas scheduler.
    """

    type = PlayerPriority.DUA
    priority = PlayerPriority.DUA.value

    def play(self):
        """
        Play the random player.

        :return:
        """
        super(RandomMediaPlayer, self).setup_media(choice(self.list_douas))

        if self.is_playing():
            self.stop()
        else:
            log.debug(
                "\tPlaying file {}".format(
                    self.currentMedia().canonicalUrl().toLocalFile()
                )
            )
            return super(RandomMediaPlayer, self).play()


class DuaAfterAthanPlayer(MediaCore):
    """
    This is a basic media player used for duas after athan.
    """

    type = PlayerPriority.DUA_AFTER_ATHAN
    priority = PlayerPriority.DUA_AFTER_ATHAN.value

    def __init__(self):
        super(DuaAfterAthanPlayer, self).__init__()

    def play(self):
        """Override"""
        super(DuaAfterAthanPlayer, self).setup_media(self._dua_after_athan)
        log.debug(
            "begin dua after athan with media {}".format(
                self.currentMedia().canonicalUrl().toLocalFile()
            )
        )
        return super(DuaAfterAthanPlayer, self).play()

    def stop(self):
        """Override"""
        return super(DuaAfterAthanPlayer, self).stop()

    def media_status_changed(self, status):
        """
        Control the state of the dua after athan player.
        In this function needs to control media player behavior only.
        Does nothing for the moment.
        :param status: new status of the current player.
        :return:
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            log.debug("finished dua after athan normally")
            pass


class AthanMediaPlayer(RegistryProperties, MediaCore):
    """
    This is the base class media player for Athan, it provides the ability to
    catch the playing start event and execute some needed functions.

    It also handles the dua after athan player.
    """

    __caller__ = ""
    type = PlayerPriority.ATHAN
    priority = PlayerPriority.ATHAN.value

    def __init__(self):
        super(AthanMediaPlayer, self).__init__()
        self.current_media = self.default_athan
        self.dua_after_athan_player = DuaAfterAthanPlayer()

    def play(self, *args, **kwargs):
        """
        Core function of athan, need to interact with other widgets when Athan begins:
            > Set the current prayer
            > Display the SysTray Panel
            > Show the 'mute' option
            > RARE: case when an athan is already playing, stop it and run athan again

        :param args:
        :param kwargs:
        :return:
        """
        self.__caller__ = kwargs.get("prayer")
        super(AthanMediaPlayer, self).setup_media(self.current_media)

        if self.is_playing() or self.dua_after_athan_player.is_playing():
            # Need to call parent's stop function
            super(AthanMediaPlayer, self).stop()
            self.dua_after_athan_player.stop()

        log.debug(
            "begin athan of prayer: {} with media {}".format(
                self.__caller__, self.currentMedia().canonicalUrl().toLocalFile()
            )
        )

        Registry().emit_signal(
            "show_systray_panel", "Athan for {} begins".format(self.__caller__)
        )

        self.prayer_frame.set_current_prayer(self.__caller__)
        self.prayer_frame.praytimes[self.__caller__].mute_cb.show()

        return super(AthanMediaPlayer, self).play()

    def stop(self):
        """
        Core function of athan, need to interact with other widgets when Athan is stopped (NOT finished):
            > Hide the 'mute' option
            > Reset normal volume to athan (in case it has been muted)
            > Close the SysTray Panel

        :return:
        """
        if not self.is_playing():
            return

        self.prayer_frame.praytimes[self.__caller__].mute_cb.hide()

        # Reset volume to normal after athan finished
        self.prayer_frame.praytimes[self.__caller__].mute_cb.setChecked(False)

        Registry().emit_signal("hide_systray_panel")

        return super(AthanMediaPlayer, self).stop()

    def media_status_changed(self, status):
        """
        Core function of athan, need to interact with other widgets when Athan is finished:
            > Hide the 'mute' option
            > Reset normal volume to athan (in case it has been muted)
            > Close the SysTray Panel
            > Check if run 'dua after athan' or not depending on settings

        :return:
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            log.debug("finished playing athan normally")
            self.prayer_frame.praytimes[self.__caller__].mute_cb.hide()

            # Reset volume to normal after athan finished
            self.prayer_frame.praytimes[self.__caller__].mute_cb.setChecked(False)

            Registry().emit_signal("hide_systray_panel")

            if Settings().value("prayer_settings/dua_after_athan") == 1:
                # TODO - Remove the stop function as the state SHOULD already be stopped here.. Need Qt fix.
                # Athan is not in stopped state here
                # Need to stop before runnning dua after athan (can cause priority issue)
                super(AthanMediaPlayer, self).stop()
                self.dua_after_athan_player.play()
        # else:
        #     log.debug("athan media status: {}".format(status))


class AthanPreviewPlayer(MediaCore):
    """
    This is a basic media player used preview athans.
    """

    type = PlayerPriority.PREVIEW_ATHAN
    priority = PlayerPriority.PREVIEW_ATHAN.value

    def __init__(self):
        super(AthanPreviewPlayer, self).__init__()

    def play(self):
        """Override"""
        return super(AthanPreviewPlayer, self).play()

    def stop(self):
        """Override"""
        return super(AthanPreviewPlayer, self).stop()

    def media_status_changed(self, status):
        """
        Control the state of the preview athan player.
        In this function needs to control media player behavior only.
        Does nothing for the moment.

        :param status: new status of the current player.
        :return:
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            pass
