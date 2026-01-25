# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 13:41:16 2026

@author: Net
"""

import socket
import struct
import numpy as np
from .proto import CORR_HDR_FMT, CORR_HDR_SIZE, MAGIC_CORR

class UdpCorrSender:
    def __init__(self, pc_ip, pc_port, max_payload=1200):
        self.addr = (pc_ip, pc_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.max_payload = int(max_payload)
        self.frame_id = 0

    def send_corr(self, corr_f32):
        corr_f32 = np.asarray(corr_f32, dtype=np.float32, order="C")
        total = corr_f32.size

        max_data_bytes = self.max_payload - CORR_HDR_SIZE
        n_per = max(1, max_data_bytes // 4)  # float32
        n_parts = (total + n_per - 1) // n_per

        fid = self.frame_id
        self.frame_id = (self.frame_id + 1) & 0xFFFFFFFF

        for part_id in range(n_parts):
            offset = part_id * n_per
            chunk = corr_f32[offset:offset + n_per]
            n_this = chunk.size
            hdr = struct.pack(CORR_HDR_FMT, MAGIC_CORR, fid, part_id, n_parts, total, offset, n_this)
            self.sock.sendto(hdr + chunk.tobytes(), self.addr)

class FrameAssembler:
    def __init__(self):
        self.frame_id = None
        self.total = None
        self.n_parts = None
        self.buf = None
        self.got = set()

    def start(self, frame_id, total, n_parts):
        self.frame_id = frame_id
        self.total = total
        self.n_parts = n_parts
        self.buf = np.empty(total, dtype=np.float32)
        self.got = set()

    def add(self, frame_id, part_id, n_parts, total, offset, n_this, data):
        if (self.frame_id != frame_id) or (self.total != total) or (self.n_parts != n_parts) or (self.buf is None):
            self.start(frame_id, total, n_parts)
        self.buf[offset:offset + n_this] = data
        self.got.add(part_id)
        return (len(self.got) == self.n_parts), self.buf
