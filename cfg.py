# -*- coding: utf-8 -*-
"""
Shared configuration for Zybo (TX/RX, DSP, UDP) and PC GUI.

- Override locally via cfg_local.py (same symbols) without touching this file.
- Used by both main_zybo.py and main_pc.py/ui.pc_gui.py.
"""

# Sampling parameters
FS = 48000.0                 # Audio sampling rate [Hz]
C_SOUND = 343.0              # Default speed of sound [m/s] (20°C); GUI can adjust

# Buffering / loop timing
FIFOSIZE = 4096              # Audio FIFO size (samples per channel)
FPS = 10.0                   # Target UI/streaming frame rate
LOOP_DT = 1.0 / FPS          # Loop period used on Zybo side

# Network endpoints (Zybo -> PC)
PC_IP = "192.168.1.1"        # PC address for receiving CORR/MEAS
ZYBO_IP = "192.168.1.103"    # Zybo address for outbound CMD target

CORR_PORT = 5005             # UDP port for correlation windows (Zybo -> PC)
MEAS_PORT = 5006             # UDP port for measurement packets (Zybo -> PC)
CMD_PORT = 6006              # UDP port for commands (PC -> Zybo)
CMD_BIND_IP = "0.0.0.0"      # Bind address on Zybo for commands

WINDOW_LEN = 512             # Correlation window length to stream
UDP_MAX_PAYLOAD = 1200       # Max UDP payload for correlation chunks

# Geometry / physical setup
MIC_SPACING_M = 0.50         # Distance between microphones [m]
# Codec/processing delay compensation (samples), applied on Zybo before sending Tx→Mic lags
# Keep zero to disable; can be overridden via GUI slider or CMD.
DELAY_COMP_SAMPLES = 0

# If True, swap L/R microphones in software (useful if wired backwards in the lab)
SWAP_MICS = True
