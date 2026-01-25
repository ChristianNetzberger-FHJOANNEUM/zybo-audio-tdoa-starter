# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:43:21 2026

@author: Net
"""

import numpy as np
import matplotlib.pyplot as plt

def plot_rx_tx_waveforms(rxright, rxleft, txref, fs=48000.0, nsamples=None, title="RX/TX Waveforms"):
    rxright = np.asarray(rxright)
    rxleft  = np.asarray(rxleft)
    txref   = np.asarray(txref)

    if nsamples is not None:
        nsamples = int(nsamples)
        rxright = rxright[:nsamples]
        rxleft  = rxleft[:nsamples]
        txref   = txref[:nsamples]

    N = min(len(rxright), len(rxleft), len(txref))
    rxright = rxright[:N]
    rxleft  = rxleft[:N]
    txref   = txref[:N]

    t_ms = (np.arange(N) / fs) * 1000.0

    def to_float(x):
        if np.issubdtype(x.dtype, np.integer):
            return x.astype(np.float32) / 32768.0
        return x.astype(np.float32)

    rxright_f = to_float(rxright)
    rxleft_f  = to_float(rxleft)
    txref_f   = to_float(txref)

    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(10, 7))
    fig.suptitle(title)

    axes[0].plot(t_ms, rxright_f); axes[0].set_ylabel("rxright"); axes[0].grid(True)
    axes[1].plot(t_ms, rxleft_f);  axes[1].set_ylabel("rxleft");  axes[1].grid(True)
    axes[2].plot(t_ms, txref_f);   axes[2].set_ylabel("txref");   axes[2].set_xlabel("time (ms)"); axes[2].grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

def plot_3_correlations(corrLR, corrTxL, corrTxR, mm_per_sample=None, title="Correlations"):
    corrLR = np.asarray(corrLR, dtype=np.float32)
    corrTxL = np.asarray(corrTxL, dtype=np.float32)
    corrTxR = np.asarray(corrTxR, dtype=np.float32)

    N = min(corrLR.size, corrTxL.size, corrTxR.size)
    corrLR = corrLR[:N]; corrTxL = corrTxL[:N]; corrTxR = corrTxR[:N]

    lags = np.arange(N, dtype=np.int32) - (N // 2)

    if mm_per_sample is None:
        x = lags.astype(np.float32); xlabel = "lag (samples)"
    else:
        x = lags.astype(np.float32) * float(mm_per_sample); xlabel = "lag distance (mm)"

    corrs = [corrLR, corrTxL, corrTxR]
    names = ["corrLR = corr(rxR, rxL)", "corrTxL = corr(txref, rxL)", "corrTxR = corr(txref, rxR)"]

    fig, axes = plt.subplots(3, 1, sharex=True, figsize=(10, 7))
    fig.suptitle(title)

    for ax, c, name in zip(axes, corrs, names):
        peak_idx = int(np.argmax(c))
        peak_lag = int(lags[peak_idx])
        peak_val = float(c[peak_idx])
        peak_x = float(x[peak_idx])

        ax.plot(x, c)
        ax.axvline(peak_x, linestyle="--")
        ax.set_ylabel("corr")
        ax.grid(True)
        ax.set_title(f"{name} | peak lag = {peak_lag:+d} samples | peak = {peak_val:.3f}")

    axes[-1].set_xlabel(xlabel)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
