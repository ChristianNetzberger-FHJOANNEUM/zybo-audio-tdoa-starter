#! /usr/bin/python3
"""
$list 2010
$comment mmap() class - emulation on Windows
"""

import mmap
import struct
import os
import numpy as np  


class RegBlock:
    def __init__(self, baseAddress, size,path = 'D:\\mem.bin'):
        self.path = path
        if os.name == 'posix':  # for Linux
            print('init REGBLOCK: {:08X} {}'.format(baseAddress,size))
            with open('/dev/mem', "r+b" ) as f:
                self.mem = mmap.mmap(f.fileno(), size, offset = baseAddress)
            if baseAddress < 0x40000000:
                print('/dev/mem exists, BASE ADDRESS INVALID!!!')
                self.mem.close()
        else:
            #for Windows PC, use a binary file at path
            if not os.path.isfile(self.path):
                memBuffer = np.arange(0x20000,dtype='int') # creat numpy array if file does not exist
                with open(self.path,'wb') as f:
                    f.write(np.ndarray.tobytes(memBuffer))    
            size = 0x10000    # min. size is 64KB for Windows
            baseAddress = 0
            print('init REGBLOCK: {:08X} {}'.format(baseAddress,size))
            with open(self.path, "r+b" ) as f:
                self.mem = mmap.mmap(f.fileno(), size,offset = baseAddress)
            
    def close(self):
        self.mem.close()
        
    def set_u32(self, address, val):
        address = address * 4
        self.mem[address:address+4] = struct.pack("<L", val & 0xffffffff)

    def get_u32(self, address):
        address = address * 4
        return struct.unpack("L", self.mem[address:address+4])[0]

    def get_i16(self, address):
        address = address * 4
        return struct.unpack("h", self.mem[address:address+2])[0],struct.unpack("h", self.mem[address+2:address+4])[0]
        
    def get_path(self):
        return self.path
