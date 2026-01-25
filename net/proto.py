# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:40:23 2026

@author: Net
"""

import struct

# CORR packet header (fragmented float32 window)
CORR_HDR_FMT = "!4sIHHIII"
CORR_HDR_SIZE = struct.calcsize(CORR_HDR_FMT)
MAGIC_CORR = b"CORR"

# MEAS packet (compact peak/lag summary)
MEAS_FMT  = "!4sIiii fff B3s"
MEAS_SIZE = struct.calcsize(MEAS_FMT)
MAGIC_MEAS = b"MEAS"
