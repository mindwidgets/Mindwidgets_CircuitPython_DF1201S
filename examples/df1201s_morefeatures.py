# SPDX-FileCopyrightText: Copyright (c) 2022 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT

import time
import board
import busio
from mindwidgets_df1201s import DF1201S

uart = busio.UART(tx=board.GP16, rx=board.GP17, baudrate=115200)

df_player = DF1201S(uart)

print("Disabling start-up prompt (persists after power off)")
df_player.disable_prompt()

print("Volume:", df_player.volume)
df_player.volume = 0.2
print("New Volume:", df_player.volume)
df_player.increase_volume(0.05)
print("Increased Volume:", df_player.volume)
df_player.decrease_volume(0.1)
print("Decreased Volume:", df_player.volume)
df_player.play_mode = DF1201S.PLAYMODE_REPEAT_ONE_SONG
print("Mode:", df_player.play_mode)

print("File Count:", df_player.total_files)

df_player.enable_led()
print("Play song")

if not df_player.play_next():
    print("No sound files to play!")

print("Current file number:", df_player.file_number)
print("Current file name: ", df_player.file_name)
print("Length of the current file in seconds:", df_player.total_time)

while df_player.playing:
    time.sleep(0.5)

print("Done playing")

df_player.disable_led()

while True:
    pass
