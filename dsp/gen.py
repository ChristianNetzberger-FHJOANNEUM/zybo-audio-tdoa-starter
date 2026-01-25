# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:39:16 2026

@author: Net
"""

import numpy as np
from typing import Optional
from .pack import pack_i16_to_i32

class Generator:
    """
    Stereo audio generator that outputs packed int32 samples:
      bits  0..15  = Left  (int16)
      bits 16..31  = Right (int16)
    """
    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.default_rng(seed)

    def stereo_zero(self, nsamples: int) -> np.ndarray:
        left_i16 = np.zeros(nsamples, dtype=np.int16)
        right_i16 = np.zeros(nsamples, dtype=np.int16)
        return pack_i16_to_i32(left_i16, right_i16)

    def stereo_sine(self, nsamples: int, m: float, n: float, amp: float = 0.9) -> np.ndarray:
        t = np.arange(nsamples, dtype=np.float64)
        left_f  = np.sin(2 * np.pi * t / float(m))
        right_f = np.sin(2 * np.pi * t / float(n))
        left_i16  = (np.clip(left_f * amp,  -1.0, 1.0) * 32767).astype(np.int16)
        right_i16 = (np.clip(right_f * amp, -1.0, 1.0) * 32767).astype(np.int16)
        return pack_i16_to_i32(left_i16, right_i16)

    def stereo_sine_harmonics(
        self,
        nsamples: int,
        m: float,
        n: float,
        amp: float = 0.9,
        nharm: int = 1,
        harm_rolloff: str = "1/k",
        seed: Optional[int] = None,
    ) -> np.ndarray:
        rng = np.random.default_rng(seed) if seed is not None else self.rng
        t = np.arange(nsamples, dtype=np.float64)

        nharm = int(max(1, nharm))
        h = np.arange(1, nharm + 1, dtype=np.float64)

        if harm_rolloff == "1/k":
            w = 1.0 / h
        elif harm_rolloff == "1/k2":
            w = 1.0 / (h ** 2)
        elif harm_rolloff == "equal":
            w = np.ones_like(h)
        else:
            raise ValueError("harm_rolloff must be one of: '1/k', '1/k2', 'equal'")

        phi_L = rng.uniform(0.0, 2.0 * np.pi, size=nharm)
        phi_R = rng.uniform(0.0, 2.0 * np.pi, size=nharm)

        left_f = np.zeros(nsamples, dtype=np.float64)
        right_f = np.zeros(nsamples, dtype=np.float64)

        for idx, harm in enumerate(h):
            left_f  += w[idx] * np.sin(2.0 * np.pi * harm * t / float(m) + phi_L[idx])
            right_f += w[idx] * np.sin(2.0 * np.pi * harm * t / float(n) + phi_R[idx])

        peak = max(np.max(np.abs(left_f)), np.max(np.abs(right_f)), 1e-12)
        left_f /= peak
        right_f /= peak

        left_i16  = (np.clip(left_f * amp,  -1.0, 1.0) * 32767).astype(np.int16)
        right_i16 = (np.clip(right_f * amp, -1.0, 1.0) * 32767).astype(np.int16)
        return pack_i16_to_i32(left_i16, right_i16)
    #STUDENT_TODO_START: Implement the AWGN , CHIRP, PRBS Generators
# HINT
    def stereo_gaussian_noise(
        self,
        nsamples: int,
        std: float = 0.2,
        amp: float = 0.9,
        seed: Optional[int] = None,
    ) -> np.ndarray:
        left_i16 = np.zeros(nsamples, dtype=np.int16)  #dummy code
        right_i16 = np.zeros(nsamples, dtype=np.int16)  #dummy code

        return pack_i16_to_i32(left_i16, right_i16)

        #def stereo_chirp()
        #def stereo_prbs()
    
    
        #STUDENT_TODO_END