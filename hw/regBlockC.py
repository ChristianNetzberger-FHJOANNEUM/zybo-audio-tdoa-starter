# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 15:00:31 2026

@author: Net
"""

import mmap
import ctypes
import os
import struct

class RegBlock:
    def __init__(self, baseAddress, size):
        self.baseAddress = baseAddress
        self.size = size
        fd = os.open("/dev/mem", os.O_RDWR | os.O_SYNC)
        try:
            self.mem = mmap.mmap(fd, size, mmap.MAP_SHARED,
                                mmap.PROT_READ | mmap.PROT_WRITE,
                                offset=baseAddress)
        finally:
            os.close(fd)

    def close(self):
        self.mem.close()

    def bind_u32(self, word_address):
        """Return a ctypes uint32 mapped to the given word address (word_address * 4 bytes)."""
        byte_off = int(word_address) * 4
        return ctypes.c_uint32.from_buffer(self.mem, byte_off)
    
    # def set_u32(self, address, val):
    #     address = address * 4
    #     self.mem[address:address+4] = struct.pack("<L", val & 0xffffffff)

    # def get_u32(self, address):
    #     address = address * 4
    #     return struct.unpack("L", self.mem[address:address+4])[0]
        
   # keep these if you still need them elsewhere
    def set_u32(self, word_address, val):
        self.bind_u32(word_address).value = (val & 0xFFFFFFFF)

    def get_u32(self, word_address):
        return self.bind_u32(word_address).value