# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:38:00 2026

@author: Net
"""
import numpy as np

def unpack_stereo_int32(packed_u32):
    """
    packed_u32: array-like uint32/int32 where:
      lower 16 bits = left (int16)
      upper 16 bits = right (int16)
    """
    p = np.asarray(packed_u32, dtype=np.uint32)
    left = (p & 0xFFFF).astype(np.int16)
    right = ((p >> 16) & 0xFFFF).astype(np.int16)
    return left, right

def pack_i16_to_i32(left_i16, right_i16):
    left_i16 = np.asarray(left_i16, dtype=np.int16)
    right_i16 = np.asarray(right_i16, dtype=np.int16)
    packed = (left_i16.astype(np.int32) & 0xFFFF) | ((right_i16.astype(np.int32) & 0xFFFF) << 16)
    return packed.astype(np.int32)

