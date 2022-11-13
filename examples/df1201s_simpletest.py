# SPDX-FileCopyrightText: Copyright (c) 2022 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT

import board
import busio
from mindwidgets_df1201s import DF1201S

uart = busio.UART(tx=board.GP16, rx=board.GP17, baudrate=115200)

df_player = DF1201S(uart)
df_player.volume = 0.2
df_player.play_mode = DF1201S.PLAYMODE_PLAY_ONCE

if not df_player.play_next():
    print("No sound files to play!")

while True:
    pass
