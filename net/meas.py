# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:41:47 2026

@author: Net
"""

import struct
from .proto import MEAS_FMT, MAGIC_MEAS

def pack_meas(frame_id, lag_lr, lag_txl, lag_txr, peak_lr, peak_txl, peak_txr, which_u8):
    return struct.pack(
        MEAS_FMT,
        MAGIC_MEAS,
        frame_id & 0xFFFFFFFF,
        int(lag_lr), int(lag_txl), int(lag_txr),
        float(peak_lr), float(peak_txl), float(peak_txr),
        int(which_u8) & 0xFF,
        b"\x00\x00\x00",
    )
