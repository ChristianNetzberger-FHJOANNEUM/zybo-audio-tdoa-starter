# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:42:19 2026

@author: Net
"""

import socket

def make_cmd_sender(zybo_ip, cmd_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (zybo_ip, cmd_port)
    return s, addr

def send_cmd(sock, addr, key, value):
    msg = f"{key}={value}".encode("ascii")
    sock.sendto(msg, addr)


def make_cmd_socket(bind_ip, cmd_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((bind_ip, cmd_port))
    s.setblocking(False)
    return s

def parse_and_apply_cmd(msg, state):
    """
    Commands are ASCII like:
      WAVE=SINE | WAVE=AWGN | WAVE=PRBS | WAVE=ZERO | WAVE=CHIRP
      M=64
      N=128
      ALPHA=0.8
      NOISE_STD=0.3
      NHARM=5
      ROLLOFF=1/k   (or 1/k2 or equal)
      SHIFT=-50
      DELAY_COMP=12   (samples, compensates codec/group delay for Tx→Mic lags)
      PLOT=LR | PLOT=TXL | PLOT=TXR
    """
    msg = msg.strip()
    if not msg or "=" not in msg:
        return False

    key, val = msg.split("=", 1)
    key = key.strip().upper()
    val = val.strip()

    try:
        if key == "WAVE":
            val_u = val.upper()
            if val_u in ("SINE", "AWGN", "PRBS", "ZERO", "CHIRP"):
                state["wave"] = val_u
                return True

        elif key == "M":
            state["m"] = float(val); return True
        elif key == "N":
            state["n"] = float(val); return True
        elif key == "ALPHA":
            state["alpha"] = float(val); return True
        elif key == "NOISE_STD":
            state["noise_std"] = float(val); return True
        elif key == "NHARM":
            state["nharm"] = int(float(val)); return True
        elif key == "ROLLOFF":
            if val in ("1/k", "1/k2", "equal"):
                state["rolloff"] = val; return True
        elif key == "SHIFT":
            state["shift"] = int(float(val)); return True
        elif key == "DELAY_COMP":
            state["delay_comp"] = int(float(val)); return True
        elif key == "PLOT":
            val_u = val.upper()
            if val_u in ("LR", "TXL", "TXR"):
                state["plot"] = val_u
                return True

    except Exception:
        return False

    return False
