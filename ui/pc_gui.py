# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:58:31 2026

@author: Net
"""

import socket
import struct
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Slider, Button, TextBox
import math
from matplotlib.patches import Circle

try:
    import cfg_local as cfg
    print("Loaded cfg_local.py")
except ModuleNotFoundError:
    import cfg as cfg
    print("Loaded cfg.py")

# use cfg.FS, cfg.PC_IP, ...
FS = cfg.FS
PC_IP = cfg.PC_IP

from net.proto import (
    CORR_HDR_FMT, CORR_HDR_SIZE, MAGIC_CORR,
    MEAS_FMT, MEAS_SIZE, MAGIC_MEAS
)
from net.udp_corr import FrameAssembler
from net.cmd import make_cmd_sender, send_cmd

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def circle_intersections(c0, r0, c1, r1):
    x0, y0 = c0
    x1, y1 = c1
    dx = x1 - x0
    dy = y1 - y0
    d = math.hypot(dx, dy)

    if d <= 1e-12:
        return []
    if d > r0 + r1:
        return []
    if d < abs(r0 - r1):
        return []

    a = (r0*r0 - r1*r1 + d*d) / (2*d)
    h_sq = r0*r0 - a*a
    if h_sq < 0:
        h_sq = 0.0
    h = math.sqrt(h_sq)

    xm = x0 + a * dx / d
    ym = y0 + a * dy / d

    rx = -dy * (h / d)
    ry =  dx * (h / d)

    p3 = (xm + rx, ym + ry)
    p4 = (xm - rx, ym - ry)

    if h < 1e-12:
        return [p3]
    return [p3, p4]

def main():
    LISTEN_CORR_PORT = cfg.CORR_PORT
    LISTEN_MEAS_PORT = cfg.MEAS_PORT
    ZYBO_IP = cfg.ZYBO_IP
    CMD_PORT = cfg.CMD_PORT

    FS = cfg.FS
    MIC_SPACING_M = cfg.MIC_SPACING_M

    rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx_sock.bind(("0.0.0.0", LISTEN_CORR_PORT))
    rx_sock.settimeout(0.02)

    meas_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    meas_sock.bind(("0.0.0.0", LISTEN_MEAS_PORT))
    meas_sock.settimeout(0.0)

    cmd_sock, cmd_addr = make_cmd_sender(ZYBO_IP, CMD_PORT)

    assembler = FrameAssembler()

    # physical scaling
    phys = {
        "c_sound": cfg.C_SOUND,
        "mm_per_sample": (cfg.C_SOUND / FS) * 1000.0,
    }

    plt.ion()
    fig = plt.figure(figsize=(10, 6))

    # Top: correlation plot
    ax = fig.add_axes([0.08, 0.58, 0.62, 0.35])
    (line,) = ax.plot([], [], label="corr")
    cursor = ax.axvline(0.0, linestyle="--", label="peak")
    info = ax.text(0.02, 0.98, "", transform=ax.transAxes, va="top")
    ax.set_title("Correlation window (selected)")
    ax.set_xlabel("Lag distance (mm)  [center ~ 0-lag]")
    ax.set_ylabel("corr")
    ax.grid(True)
    ax.legend(loc="upper right")

    # Bottom: 2D geometry
    ax_geo = fig.add_axes([0.08, 0.12, 0.62, 0.33])
    ax_geo.set_title("2D geometry: circles (TOA) + rays (TDOA/TOA)")
    ax_geo.grid(True)
    ax_geo.set_aspect("equal", adjustable="datalim")
    ax_geo.set_xlim(-0.35, 0.35)
    ax_geo.set_ylim(-0.15, 0.60)
    ax_geo.set_xlabel("x (m)")
    ax_geo.set_ylabel("y (m)")

    # Microphones
    L = MIC_SPACING_M
    micL = (-L / 2.0, 0.0)
    micR = ( L / 2.0, 0.0)
    mic_radius = 0.03

    ax_geo.add_patch(Circle(micL, mic_radius, fill=False, linewidth=2))
    ax_geo.add_patch(Circle(micR, mic_radius, fill=False, linewidth=2))
    ax_geo.text(micL[0], micL[1] - 0.07, "Mic L", ha="center")
    ax_geo.text(micR[0], micR[1] - 0.07, "Mic R", ha="center")
    ax_geo.plot([micL[0], micR[0]], [0.0, 0.0], linewidth=1)
    ax_geo.plot([0], [0], marker="o")

    circleL_line, = ax_geo.plot([], [], linewidth=1, linestyle="-", label="rL (Tx→MicL)")
    circleR_line, = ax_geo.plot([], [], linewidth=1, linestyle="-", label="rR (Tx→MicR)")
    inter_pt, = ax_geo.plot([], [], marker="x", markersize=10, linestyle="None", label="intersection")

    ray_len = 0.8
    ray_tdoa, = ax_geo.plot([0, 0], [0, ray_len], linestyle="--", linewidth=2, label="TDOA ray (LR)")
    ray_toa,  = ax_geo.plot([0, 0], [0, ray_len], linestyle=":",  linewidth=2, label="TOA ray (from circles)")

    geo_text = ax_geo.text(0.02, 0.95, "", transform=ax_geo.transAxes, va="top")
    ax_geo.legend(loc="lower right")

    # Controls
    ax_radio = fig.add_axes([0.76, 0.70, 0.24, 0.18])
    radio = RadioButtons(ax_radio, ("SINE", "AWGN", "PRBS", "CHIRP"), active=0)
    ax_radio.set_title("Waveform")

    ax_plot = fig.add_axes([0.76, 0.54, 0.24, 0.12])
    radio_plot = RadioButtons(ax_plot, ("LR", "TXL", "TXR"), active=0)
    ax_plot.set_title("Plot CORR")

    ax_alpha = fig.add_axes([0.78, 0.42, 0.2, 0.025])
    s_alpha = Slider(ax_alpha, "alpha", 0.0, 1.0, valinit=1.0)

    ax_noise = fig.add_axes([0.78, 0.38, 0.2, 0.025])
    s_noise = Slider(ax_noise, "noise_std", 0.0, 1.0, valinit=0.3)

    ax_m = fig.add_axes([0.78, 0.34, 0.2, 0.025])
    s_m = Slider(ax_m, "m (period)", 8.0, 1024.0, valinit=64.0, valstep=1.0)

    ax_n = fig.add_axes([0.78, 0.30, 0.2, 0.025])
    s_n = Slider(ax_n, "n (period)", 8.0, 1024.0, valinit=64.0, valstep=1.0)

    ax_nharm = fig.add_axes([0.78, 0.26, 0.2, 0.025])
    s_nharm = Slider(ax_nharm, "nharm", 1.0, 16.0, valinit=1.0, valstep=1.0)

    ax_shift = fig.add_axes([0.78, 0.22, 0.2, 0.025])
    s_shift = Slider(ax_shift, "shift", -500.0, 500.0, valinit=0.0, valstep=1.0)

    ax_delay = fig.add_axes([0.78, 0.18, 0.2, 0.025])
    s_delay = Slider(
        ax_delay,
        "delay_comp (samp)",
        -50.0,
        50.0,
        valinit=getattr(cfg, "DELAY_COMP_SAMPLES", 0),
        valstep=1.0,
    )

    ax_send = fig.add_axes([0.76, 0.06, 0.11, 0.06])
    b_send = Button(ax_send, "Send")

    ax_zero = fig.add_axes([0.87, 0.06, 0.11, 0.06])
    b_zero = Button(ax_zero, "Zero")

    ax_temp = fig.add_axes([0.76, 0.00, 0.22, 0.05])
    tb_temp = TextBox(ax_temp, "Temp °C", initial="20")

    current_wave = {"name": "SINE"}
    current_plot = {"which": "LR"}

    def on_wave(label):
        current_wave["name"] = label
        send_cmd(cmd_sock, cmd_addr, "WAVE", current_wave["name"])
    radio.on_clicked(on_wave)

    def on_plot(label):
        current_plot["which"] = label.upper()
        send_cmd(cmd_sock, cmd_addr, "PLOT", current_plot["which"])
    radio_plot.on_clicked(on_plot)

    # Immediate updates for sliders
    def on_alpha(val):
        send_cmd(cmd_sock, cmd_addr, "ALPHA", f"{val:.3f}")
    s_alpha.on_changed(on_alpha)

    def on_noise(val):
        send_cmd(cmd_sock, cmd_addr, "NOISE_STD", f"{val:.3f}")
    s_noise.on_changed(on_noise)

    def on_m(val):
        send_cmd(cmd_sock, cmd_addr, "M", f"{val:.1f}")
    s_m.on_changed(on_m)

    def on_n(val):
        send_cmd(cmd_sock, cmd_addr, "N", f"{val:.1f}")
    s_n.on_changed(on_n)

    def on_nharm(val):
        send_cmd(cmd_sock, cmd_addr, "NHARM", f"{int(val)}")
    s_nharm.on_changed(on_nharm)

    def on_shift(val):
        send_cmd(cmd_sock, cmd_addr, "SHIFT", f"{int(val)}")
    s_shift.on_changed(on_shift)

    def on_delay(val):
        send_cmd(cmd_sock, cmd_addr, "DELAY_COMP", f"{int(val)}")
    s_delay.on_changed(on_delay)

    def update_temp(text):
        try:
            T = float(text)
            c = 331.3 + 0.606 * T
            phys["c_sound"] = c
            phys["mm_per_sample"] = (c / FS) * 1000.0
        except Exception:
            pass
    tb_temp.on_submit(update_temp)

    # Send on change helpers (also used by Send/Zero)
    def send_all():
        send_cmd(cmd_sock, cmd_addr, "WAVE", current_wave["name"])
        send_cmd(cmd_sock, cmd_addr, "ALPHA", f"{s_alpha.val:.3f}")
        send_cmd(cmd_sock, cmd_addr, "NOISE_STD", f"{s_noise.val:.3f}")
        send_cmd(cmd_sock, cmd_addr, "M", f"{s_m.val:.1f}")
        send_cmd(cmd_sock, cmd_addr, "N", f"{s_n.val:.1f}")
        send_cmd(cmd_sock, cmd_addr, "NHARM", f"{int(s_nharm.val)}")
        send_cmd(cmd_sock, cmd_addr, "SHIFT", f"{int(s_shift.val)}")
        send_cmd(cmd_sock, cmd_addr, "DELAY_COMP", f"{int(s_delay.val)}")
        send_cmd(cmd_sock, cmd_addr, "PLOT", current_plot["which"])

    def on_send(_event):
        send_all()

    def on_zero(_event):
        radio.set_active(0)
        radio_plot.set_active(0)
        s_alpha.set_val(1.0)
        s_noise.set_val(0.3)
        s_m.set_val(64.0)
        s_n.set_val(64.0)
        s_nharm.set_val(1.0)
        s_shift.set_val(0.0)
        s_delay.set_val(getattr(cfg, "DELAY_COMP_SAMPLES", 0))
        current_wave["name"] = "SINE"
        current_plot["which"] = "LR"
        send_all()

    b_send.on_clicked(on_send)
    b_zero.on_clicked(on_zero)

    print(f"Listening CORR UDP :{LISTEN_CORR_PORT} | MEAS UDP :{LISTEN_MEAS_PORT} | CMD -> {ZYBO_IP}:{CMD_PORT}")

    meas = {"lag_lr": 0, "lag_txl": 0, "lag_txr": 0, "peak_lr": 0.0, "peak_txl": 0.0, "peak_txr": 0.0}
    meas_count = 0
    corr_count = 0
    ylo, yhi = None, None

    def make_circle_xy(center, r, n=200):
        ang = np.linspace(0, 2*np.pi, n, endpoint=True)
        x = center[0] + r*np.cos(ang)
        y = center[1] + r*np.sin(ang)
        return x, y

    while True:
        # MEAS
        while True:
            try:
                pkt, _ = meas_sock.recvfrom(256)
            except BlockingIOError:
                break
            except Exception:
                break

            if len(pkt) != MEAS_SIZE:
                continue

            magic2, frame_id2, lag_lr, lag_txl, lag_txr, peak_lr, peak_txl, peak_txr, which_u8, _pad = struct.unpack(MEAS_FMT, pkt)
            if magic2 != MAGIC_MEAS:
                continue

            meas["lag_lr"] = int(lag_lr)
            meas["lag_txl"] = int(lag_txl)
            meas["lag_txr"] = int(lag_txr)
            meas["peak_lr"] = float(peak_lr)
            meas["peak_txl"] = float(peak_txl)
            meas["peak_txr"] = float(peak_txr)
            meas_count += 1

        # CORR
        for _ in range(50):
            try:
                pkt, _ = rx_sock.recvfrom(8192)
            except socket.timeout:
                break

            if len(pkt) < CORR_HDR_SIZE:
                continue

            magic, frame_id, part_id, n_parts, total, offset, n_this = struct.unpack(CORR_HDR_FMT, pkt[:CORR_HDR_SIZE])
            if magic != MAGIC_CORR:
                continue

            data = np.frombuffer(pkt[CORR_HDR_SIZE:], dtype=np.float32, count=n_this)
            complete, corr = assembler.add(frame_id, part_id, n_parts, total, offset, n_this, data)

            if complete:
                corr_count += 1
                N = corr.size
                lags_samples = np.arange(N, dtype=np.int32) - (N // 2)
                x_mm = lags_samples * phys["mm_per_sample"]

                peak_idx = int(np.argmax(corr))
                peak_lag_samp = int(lags_samples[peak_idx])
                peak_mm = float(peak_lag_samp * phys["mm_per_sample"])

                line.set_data(x_mm, corr)
                cursor.set_xdata([peak_mm, peak_mm])
                ax.set_xlim(float(x_mm[0]), float(x_mm[-1]))

                cur_lo = float(np.min(corr))
                cur_hi = float(np.max(corr))
                if cur_lo == cur_hi:
                    cur_lo -= 1.0
                    cur_hi += 1.0
                if ylo is None:
                    ylo, yhi = cur_lo, cur_hi
                else:
                    a = 0.2
                    ylo = (1-a)*ylo + a*cur_lo
                    yhi = (1-a)*yhi + a*cur_hi
                pad = 0.05*(yhi-ylo)
                ax.set_ylim(ylo-pad, yhi+pad)

                # Geometry (MEAS)
                delta_m = (meas["lag_lr"] * phys["mm_per_sample"]) / 1000.0
                ratio = clamp(delta_m / MIC_SPACING_M, -1.0, 1.0)
                theta_tdoa = math.asin(ratio)
                theta_tdoa_deg = theta_tdoa * 180.0 / math.pi

                dx1 = math.sin(theta_tdoa)
                dy1 = math.cos(theta_tdoa)
                ray_tdoa.set_data([0.0, dx1 * ray_len], [0.0, dy1 * ray_len])

                rL = abs(meas["lag_txl"]) * (phys["c_sound"] / FS)
                rR = abs(meas["lag_txr"]) * (phys["c_sound"] / FS)

                xcl, ycl = make_circle_xy(micL, rL)
                xcr, ycr = make_circle_xy(micR, rR)
                circleL_line.set_data(xcl, ycl)
                circleR_line.set_data(xcr, ycr)

                pts = circle_intersections(micL, rL, micR, rR)
                chosen = None
                if len(pts) == 1:
                    chosen = pts[0]
                elif len(pts) == 2:
                    pA, pB = pts
                    chosen = pA if pA[1] >= pB[1] else pB

                if chosen is not None:
                    inter_pt.set_data([chosen[0]], [chosen[1]])
                    ang_toa = math.atan2(chosen[0], chosen[1])
                    dx2 = math.sin(ang_toa)
                    dy2 = math.cos(ang_toa)
                    ray_toa.set_data([0.0, dx2 * ray_len], [0.0, dy2 * ray_len])
                else:
                    inter_pt.set_data([], [])
                    ray_toa.set_data([0.0, 0.0], [0.0, ray_len])

                m = float(s_m.val)
                f_hz = FS / m
                lambda_cm = (phys["c_sound"] / f_hz) * 100.0

                geo_text.set_text(
                    f"TDOA: Δd={delta_m:+.3f} m  θ={theta_tdoa_deg:+.1f}°\n"
                    f"TOA radii: rL={rL:.3f} m  rR={rR:.3f} m\n"
                    f"m={m:.0f} -> f={f_hz:.1f} Hz  λ={lambda_cm:.1f} cm"
                )

                info_text = (
                    f"cnt: corr={corr_count} meas={meas_count}\n"
                    f"CORR peak: {peak_lag_samp:+d} samples ({peak_mm:+.1f} mm)\n"
                    f"MEAS lags: LR={meas['lag_lr']}  TxL={meas['lag_txl']}  TxR={meas['lag_txr']}\n"
                    f"peaks: LR={meas['peak_lr']:.3f}  TxL={meas['peak_txl']:.3f}  TxR={meas['peak_txr']:.3f}\n"
                    f"delay_comp={int(s_delay.val)} samp"
                )
                info.set_text(info_text)
            else:
                # Keep counters visible even if no complete corr this loop
                info.set_text(f"cnt: corr={corr_count} meas={meas_count}")

        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.01)
