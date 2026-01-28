# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 09:50:43 2026

@author: Net
"""

import numpy as np
import hw.regs as reg


def setreg(ip_mmap,shadow_regs,sigaddr,value):
    regaddr = sigaddr[0]
    slice_start = sigaddr[1]
    slice_range = sigaddr[2]-sigaddr[1]+1
    mask  = (1 << slice_range)-1    # calculate mask for the regslice
    shadow_regs[regaddr] &= ~(mask << slice_start)
    shadow_regs[regaddr] |= (value << slice_start)
    ip_mmap.set_u32(regaddr,shadow_regs[regaddr]) 
    return

def getreg(ip_mmap,sigaddr):
    regaddr = sigaddr[0]
    slice_start = sigaddr[1]
    slice_range = sigaddr[2]-sigaddr[1]+1
    mask  = (1 << slice_range)-1    # calculate mask for the regslice
    value = ip_mmap.get_u32(regaddr)
    value = (value >> slice_start)
    value &= mask
    return value

class HwVersion():
    def __init__(self,ip_mmap,shadow_regs):
        self.regAddr        = reg.identifier[0]
        self.shadow_regs    = shadow_regs
        self.ip_mmap         = ip_mmap

    def get(self):
        value = getreg(self.ip_mmap, reg.identifier)
        return value
 
class Sliders():
    def __init__(self,ip_mmap,shadow_regs, slider_number = -1):
        self.sliderNumber   = slider_number
        self.regAddr        = reg.sliders[0]
        self.shadow_regs    = shadow_regs
        self.regSlice       = reg.sliders[1:]
        self.ip_mmap         = ip_mmap

    def get(self):
        value = getreg(self.ip_mmap, reg.sliders)
        if self.sliderNumber < 0:
            return  value     
        else:
            return  value   & (1<<self.sliderNumber)      

    def get_config(self):
        return self.ip_mmap,self.regSlice

class Buttons():
    def __init__(self,ip_mmap,shadow_regs, button_number = -1):
        self.buttonNumber   = button_number
        self.regAddr        = reg.buttons[0]
        self.shadow_regs    = shadow_regs
        self.regSlice       = reg.buttons[1:]
        self.ip_mmap         = ip_mmap

    def get(self):
        if self.regAddr < 0:
            return 0
        else: # extract the slice range from the register value
           value = getreg(self.ip_mmap, reg.sliders_reg)
           if self.buttonNumber < 0:
                return  value     
           else:
                return  value & (1<<self.buttonNumber)      

class Buzzer():
    def __init__(self,ip_mmap,shadow_regs):
        self.regAddr        = reg.buzzer_reg
        self.regSlice       = reg.buzzer_reg[1:]
        self.ip_mmap         = ip_mmap
        self.shadow_regs    = shadow_regs
        self.state = False
        self.value = False
        
    def set_state(self,state): # buzzer can be on or off
        self.state = state
        if state:
            self.shadow_regs[self.regAddr] &= ~0x3
            self.shadow_regs[self.regAddr] |= 0x1
        else:
            self.shadow_regs[self.regAddr] &= ~0x3
        self.ip_mmap.set_u32(self.regAddr,self.shadow_regs[self.regAddr]) 
        
    def toggle(self):
        self.value = not self.value
        if self.value:
            self.shadow_regs[self.regAddr] |= 0x10
        else:
            self.shadow_regs[self.regAddr] &= ~0x10
        self.ip_mmap.set_u32(self.regAddr,self.shadow_regs[self.regAddr]) 

    def get_config(self):
        return self.ip_mmap,self.regSlice

class Leds():
    def __init__(self,ip_mmap,shadow_regs):
        self.regAddr        = reg.leds[0]
        self.regSlice       = reg.leds[1:]
        self.ip_mmap         = ip_mmap
        self.shadow_regs    = shadow_regs
        
    def set(self,value): # led can be on or off
        setreg(self.ip_mmap, self.shadow_regs, reg.leds,value)

    def get_config(self):
        return self.ip_mmap,self.regSlice

"""Reg definitions for the audio peripherals
fxgen_level           = (0x02,0,15)   # function generator signal level
fxgen_offset          = (0x02,16,31)  # function generator signal offset
fxgen_fcw             = (0x03,0,31)   # function generator frequency control word
fxgen_wavsel          = (0x04,0,3)    # function generator waveform selection
audio_select          = (0x04,4,4)    # select audio for audio dsp input
line_select           = (0x04,5,5)    # select line in
mic_select            = (0x04,6,6)    # select microphone in
test_in_left          = (0x04,8,8)    # force test signal on left audio input
test_in_right         = (0x04,9,9)    # force test signal on right audio input
test_out_left         = (0x04,10,10)  # force test signal on left audio output
test_out_right        = (0x04,11,11)  # force test signal on right audio output
audio_loop_en         = (0x04,7,7)    # enable audio loop
audio_in_scale        = (0x04,12,15)  # barrel shifter to amplify audio input
audio_mute_left       = (0x04,16,16)  # mute left audio out
audio_mute_right      = (0x04,17,17)  # mute right audio out

fifo2_rdata           = (0x1E,0,31)   # audio fifo read data
fifo2_rd_stb          = (0x1E,0,0)    # audio fifo read strobe
fifo2_wdata           = (0x1E,0,31)   # audio fifo write data
fifo2_wr_stb          = (0x1E,0,0)    # audio fifo write strobe
fifo2_en              = (0x1F,0,0)    # audio fifo enable
fifo2_reset           = (0x1F,1,1)    # audio fifo_reset
fifo2_rxtrig          = (0x1F,2,2)    # audio fifo receive trigger
fifo2_rx_stream       = (0x20,3,3)    # audio fifo read continuous stream
fifo2_tx_size         = (0x20,0,15)   # audio fifo  size in tx path
fifo2_tx_waddr        = (0x20,16,31)  # audio fifo write address in tx path
fifo2_rx_size         = (0x21,0,15)   # audio fifo size in rx path
fifo2_rx_waddr        = (0x21,16,31)  # audio fifo write address in tx path
"""
class Audio():
    def __init__(self,ip_mmap,shadow_regs):
        self.ip_mmap         = ip_mmap
        self.shadow_regs    = shadow_regs
        self._fifo_u32 = self.ip_mmap.bind_u32(reg.fifo2_rdata[0])  # fifo_reg[0] is your word address
    #example methods
    def mic_activate(self):
        setreg(self.ip_mmap, self.shadow_regs, reg.mic_select,1)
        return            
    def line_activate(self):
        setreg(self.ip_mmap, self.shadow_regs,reg.line_select,1)
        return    
    #STUDENT_TODO_START:
# HINT
    # add remaining methods for the audio interface here 
    # 
    # 
    # 
    #    
    
    #STUDENT_TODO_END:
 