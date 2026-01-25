# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:38:41 2026

@author: Net
"""
import numpy as np

def cyclic_crosscorr_fft(x, y, normalize=True, demean=True):
    """
    Cyclic cross-correlation via FFT + IFFT, returned FFTSHIFTED (zero-lag at center).
    """
    #STUDENT_TODO_START: Implement the cyclic cross-correlation function
# HINT
    # The cyclic cross-correlation function is implemented using the FFT.
    # The FFT is used to convert the time domain signals into the frequency domain.
    # The cross-correlation is then computed in the frequency domain.
    # The inverse FFT is used to convert the cross-correlation back into the time domain.
    # The result is returned as a numpy array.
    
#STUDENT_TODO_END 

def peak_lag_of_fftshifted_corr(corr):
    corr = np.asarray(corr)
    N = corr.size
    idx = int(np.argmax(corr))
    lag = idx - (N // 2)
    peak = float(corr[idx])
    return lag, peak

def slice_around_center(arr, win_len):
    arr = np.asarray(arr)
    N = arr.size
    half = int(win_len) // 2
    mid = N // 2
    return arr[mid-half:mid+half]
  

