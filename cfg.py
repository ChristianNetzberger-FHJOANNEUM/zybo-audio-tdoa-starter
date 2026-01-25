# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:32:58 2026

@author: Net
"""
#HELLO OLD TEXT
# Shared configuration (both sides)

FS = 48000.0
C_SOUND = 343.0

FIFOSIZE = 4096
FPS = 10.0
LOOP_DT = 1.0 / FPS

# Network
PC_IP = "192.168.1.1"
ZYBO_IP = "192.168.1.103"

CORR_PORT = 5005
MEAS_PORT = 5006
CMD_PORT = 6006
CMD_BIND_IP = "0.0.0.0"

WINDOW_LEN = 512
UDP_MAX_PAYLOAD = 1200

MIC_SPACING_M = 0.50
# Codec/processing delay compensation (in samples), applied on Zybo before
# sending TOA lags. Keep zero to disable.
DELAY_COMP_SAMPLES = 0

# Swap microphones (treat physical right as logical left and vice versa)
SWAP_MICS = True
