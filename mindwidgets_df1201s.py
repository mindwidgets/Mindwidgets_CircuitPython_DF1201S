# SPDX-FileCopyrightText: Copyright (c) 2022 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT
"""
`mindwidgets_df1201s`
================================================================================

CircuitPython driver for DFRobot DFPlayer Pro (DF1201S) MP3 player with onboard storage


* Author(s): Aaron Silinskas

Implementation Notes
--------------------

**Hardware:**

* `Product Page <https://www.dfrobot.com/product-2232.html>`_
* `Wiki <https://wiki.dfrobot.com/DFPlayer_PRO_SKU_DFR0768>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""

# Imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/mindwidgets/Mindwidgets_CircuitPython_DF1201S.git"

import busio
from micropython import const

# Private constants
_DFPLAYER_VOLUME_MAX = const(30)
_OK_RESPONSE = "OK"


class DF1201S(object):
    """Driver for DFRobot DFPlayer Pro (DF1201S) MP3 player with onboard storage."""

    PLAYMODE_REPEAT_ONE_SONG = const(1)
    """play_mode: Repeat one sound."""
    PLAYMODE_REPEAT_ALL = const(2)
    """play_mode: Repeat all sounds."""
    PLAYMODE_PLAY_ONCE = const(3)
    """play_mode: Play one sound and pause."""
    PLAYMODE_RANDOM = const(4)
    """play_mode: Play a random sound."""
    PLAYMODE_REPEAT_FOLDER = const(5)
    """play_mode: Play all sounds in a folder."""

    def __init__(self, uart: busio.UART) -> None:
        """
        Initialize the DFPlayer connection.

        :param busio.UART uart: the serial connection to the DFPlayer 
        """
        self._uart = uart
        if not self.connected:
            raise Exception("DFPlayer could not be initialized.")

    def _send_query(self, command: str, arg=None) -> str:
        """
        Send AT command and return the response.

        :param str command: the command to send (without AT prefix or CR\LF)
        :param arg: optional command argument
        :return: the response to the command (CR\LF removed)
        """
        # format the AT command, adding the argument if given
        at_command = "AT"
        if command != "":
            if arg != None:
                at_command = f"AT+{command}={arg}"
            else:
                at_command = f"AT+{command}"

        print("DFPlayer Command: ", at_command)

        # send the AT command
        self._uart.write(bytearray(f"{at_command}\r\n"))

        # read the response and strip the \r\n
        response = self._uart.readline()

        parsed = "" if response == None else str(response[0:-2], 'ascii')

        print("DFPlayer Response: ", parsed)

        return parsed

    def _send_command(self, command: str, arg=None) -> bool:
        """
        Send AT command and return true for an OK response.

        :param str command: the command to send (without AT prefix or CR\LF)
        :param arg: optional command argument
        :return: True if the command was successful
        """
        return self._send_query(command, arg) == _OK_RESPONSE

    def _unwrap_int(self, value: str) -> int:
        """
        Convert a string to an int if it only contains digits, otherwise return -1.

        :param str value: the string to attempt to convert to an int
        :return: the int value of the string, or -1 if it could not be converted
        """
        if value.isdigit():
            return int(value)
        return -1

    def _map_volume(self, volume: float) -> int:
        """
        Map 0.0 to 1.0 volume value to DFPlayer's volume range.

        :param float volume: the volume, from 0 to 1, to convert
        :return: the volume mapped to a valid DFPlayer Pro volume value
        """
        return max(min(int(volume * _DFPLAYER_VOLUME_MAX), _DFPLAYER_VOLUME_MAX), 0)

    @property
    def connected(self) -> bool:
        """True if the DFPlayer is connected."""
        return self._send_command("")

    def set_baud_rate(self, rate: int) -> bool:
        """
        Set baud rate for the serial DFPlayer connection.        

        .. note:: Persists after power off.

        :param int rate: the baud rate to use.
            Valid values are 9600、19200、38400、57600、or 115200.
        :return: True if the baud rate was set.
        """
        return self._send_command("BAUDRATE", rate)

    @property
    def volume(self) -> float:
        """Volume level, as a float between 0 and 1."""
        response = self._send_query("VOL", "?")
        df_volume = self._unwrap_int(response[7:-1])
        if df_volume < 0:
            return 0

        return float(df_volume) / 30.0

    @volume.setter
    def volume(self, volume: float) -> bool:
        """
        Set the volume level.

        .. note:: Persists after power off.

        :param float volume: the volume level, as a float between 0 and 1.
        :return: True if the volume was set.
        """
        df_volume = self._map_volume(volume)
        return self._send_command("VOL", df_volume)

    def increase_volume(self, increment: float) -> bool:
        """
        Increase the volume level.

        .. note:: Persists after power off.

        :param float increment: the amount to increase the volume, as a float between 0 and 1.
        :return: True if the volume was increased.
        """
        df_volume = self._map_volume(increment)
        return self._send_command("VOL", f"+{df_volume}")

    def decrease_volume(self, decrement: float) -> bool:
        """
        Decrease the volume level.

        .. note:: Persists after power off.

        :param float decrement: the amount to decrement the volume, as a float between 0 and 1.
        :return: True if the volume was decreased.
        """
        df_volume = self._map_volume(decrement)
        return self._send_command("VOL", f"-{df_volume}")

    def enable_led(self) -> bool:
        """
        Turn the builtin LED on.

        .. note:: Persists after power off.

        :return: True if the LED is on.
        """
        return self._send_command("LED", "ON")

    def disable_led(self) -> bool:
        """
        Turn the builtin LED off.

        .. note:: Persists after power off.

        :return: True if the LED is off.
        """
        return self._send_command("LED", "OFF")

    def enable_prompt(self) -> bool:
        """
        Enable the sound that is played after power on.

        .. note:: Persists after power off.

        :return: True if the prompt is enabled.
        """
        return self._send_command("PROMPT", "ON")

    def disable_prompt(self) -> bool:
        """
        Disable the sound that is played after power on.

        .. note:: Persists after power off.

        :return: True if the prompt is disabled.
        """
        return self._send_command("PROMPT", "OFF")

    def enable_amp(self) -> bool:
        """
        Enable the builtin amplifier.

        :return: True if the amp is enabled.
        """
        return self._send_command("AMP", "ON")

    def disable_amp(self) -> bool:
        """
        Disable the builtin amplifier.

        :return: True if the amp is disabled.
        """
        return self._send_command("AMP", "OFF")

    @property
    def play_mode(self) -> int:
        """
        Returns the current play mode.

        :return: One of the play mode constants (`PLAYMODE_REPEAT_ONE_SONG`, `PLAYMODE_REPEAT_ALL`, or `PLAYMODE_PLAY_ONCE`).
            `PLAYMODE_RANDOM` can be set, but this function will return -1. Bug in the device?
            `PLAYMODE_REPEAT_FOLDER` can be set, but this function will return 3. Bug in the device?

        """
        response = self._send_query("PLAYMODE", "?")
        return self._unwrap_int(response[10:])

    @play_mode.setter
    def play_mode(self, new_mode: int) -> bool:
        """
        Set the play mode.

        :param int new_mode: One of `PLAYMODE_REPEAT_ONE_SONG`, `PLAYMODE_REPEAT_ALL`, `PLAYMODE_PLAY_ONCE`, `PLAYMODE_RANDOM`, or `PLAYMODE_REPEAT_FOLDER`.
        :return: True if the play mode was set.
        """
        return self._send_command("PLAYMODE", new_mode)

    def play_next(self) -> bool:
        """
        Play the next sound.

        :return: True if the next sound is playing.
        """
        return self._send_command("PLAY", "NEXT")

    def play_last(self) -> bool:
        """
        Play the last sound.

        :return: True if the last sound is playing.
        """
        return self._send_command("PLAY", "LAST")

    def play_file_number(self, file_number: int) -> bool:
        """
        Play the sound at the given file number.

        .. note:: Plays the first sound if the file number is invalid. I don't see a way to turn off this behavior.

        :param int file_number: the file number to play.
        :return: True if the given file number is playing, False if the first file is playing.
        """
        return self._send_command("PLAYNUM", file_number)

    def play_file_name(self, file_name: str) -> bool:
        """
        Play the sound with the given file name.

        .. note:: Plays the first sound if the file name is invalid. I don't see a way to turn off this behavior.

        :param str file_name: the file name to play.
        :return: True if the given file is playing, False if the first file if playing.
        """
        return self._send_command("PLAYFILE", file_name)

    def fast_forward(self, seconds: int) -> bool:
        """
        Fast forward the currently playing sound.

        :param int seconds: the number of seconds to fast forward.
        :return: True if fast forward was successful.
        """
        return self._send_command("TIME", f"+{seconds}")

    def fast_rewind(self, seconds: int) -> bool:
        """
        Rewind the currently playing sound.

        :param int seconds: the number of seconds to rewind.
        :return: True if rewind was successful.
        """
        return self._send_command("TIME", f"-{seconds}")

    def fast_seek(self, seconds: int) -> bool:
        """
        Start playing the current sound at a specific time offset.

        .. note:: If the offset exceeds the sound length, this function still returns `True` and the sound stops.

        :param int seconds: the time offset, in seconds.
        :return: True if the current offset was set. 
        """
        return self._send_command("TIME", seconds)

    @property
    def total_files(self) -> int:
        """The total count of sound files available."""
        return self._unwrap_int(self._send_query("QUERY", 2))

    @property
    def file_number(self) -> int:
        """The file number of the currently playing file."""
        return self._unwrap_int(self._send_query("QUERY", 1))

    @property
    def file_name(self) -> str:
        """The file name of the currently playing file."""
        return self._send_query("QUERY", 5)

    @property
    def played_time(self) -> int:
        """The number of seconds the current sound has played."""
        return self._unwrap_int(self._send_query("QUERY", 3))

    @property
    def total_time(self) -> int:
        """The length of the current sound in seconds."""
        return self._unwrap_int(self._send_query("QUERY", 4))

    @property
    def playing(self) -> bool:
        """True if a sound is currently playing."""
        return self.played_time < self.total_time
