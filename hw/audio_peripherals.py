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
        if self.regAddr < 0:
            return 0
        else:
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
        setreg(self.ip_mmap, self.shadow_regs, reg.leds,1)

    def get_config(self):
        return self.ip_mmap,self.regSlice

class Audio():
    def __init__(self,ip_mmap,shadow_regs):
        self.ip_mmap         = ip_mmap
        self.shadow_regs    = shadow_regs
        self._fifo_u32 = self.ip_mmap.bind_u32(reg.fifo2_rdata[0])  # fifo_reg[0] is your word address
    
    def mic_activate(self):
        setreg(self.ip_mmap, self.shadow_regs, reg.mic_select,1)
        return            
    def line_activate(self):
        setreg(self.ip_mmap, self.shadow_regs,reg.line_select,1)
        return            
    def audio_select(self,value):
        setreg(self.ip_mmap, self.shadow_regs,reg.audio_select,value)
        return            
    def audio_mute(self,left,right):
        setreg(self.ip_mmap, self.shadow_regs,reg.audio_mute_left,left)
        setreg(self.ip_mmap, self.shadow_regs,reg.audio_mute_right,right)
        return            
    def audio_loop(self,value):
        setreg(self.ip_mmap, self.shadow_regs,reg.audio_loop_en,value)
        return            
    def audio_in_scale(self,value):
        setreg(self.ip_mmap, self.shadow_regs,reg.audio_in_scale,value)
        return            
    def test_out(self,left,right):
        setreg(self.ip_mmap, self.shadow_regs,reg.test_out_left,left)
        setreg(self.ip_mmap, self.shadow_regs,reg.test_out_right,right)
        return            
    def fxgen_frequency(self,freq):
        setreg(self.ip_mmap, self.shadow_regs,reg.fxgen_fcw,freq*42000)
        return  
    def fxgen_wavsel(self,value):
        setreg(self.ip_mmap, self.shadow_regs,reg.fxgen_wavsel,value)  
        return  
        return
    def fxgen_level(self,value):
        setreg(self.ip_mmap, self.shadow_regs,reg.fxgen_level,value) 
        return
    def fifo_send(self,txdata):
        print(f"'FIFO Write: before write: waddr={self.get_fifo_waddr()}, wrsize={self.get_fifo_wrsize()}, rdsize={self.get_fifo_rdsize()}")
        self.fifo_enable(1)
        # for i in range(txdata.size):
        #     self._setreg(self.regs, self.shadow_regs,fifo_reg,txdata[i])
        tx = np.asarray(txdata, dtype=np.uint32)  # avoids numpy int32 negatives etc.
        fifo = self._fifo_u32                     # local var for speed
        for v in tx.tolist():                     # Python ints iterate fast
            fifo.value = v
        self.fifo_enable(1)
        print(f"'FIFO Write: after write: waddr={self.get_fifo_waddr()}, wrsize={self.get_fifo_wrsize()}, rdsize={self.get_fifo_rdsize()}")
        print("sent",txdata.size,"Audio Samples")
        return    
    def fifo_receive(self,nsamples):
        fifo = self._fifo_u32
        data = [0] * nsamples
        for i in range(nsamples):
            data[i] = fifo.value
    
        rx = np.array(data, dtype=np.uint32)
        return rx

    def fifo_enable(self,value):       
        setreg(self.ip_mmap, self.shadow_regs,reg.fifo2_en,value) 
        return
    def fifo_reset(self,value):       
        setreg(self.ip_mmap, self.shadow_regs,reg.fifo2_reset,value) 
        return
    def fifo_rxtrigger(self):       
        setreg(self.ip_mmap, self.shadow_regs,reg.fifo2_rxtrig,1) 
        return
    def get_fifo_wrsize(self):
        value  = getreg(self.ip_mmap, reg.fifo2_wr_size)
        return(value)
    def get_fifo_rdsize(self):
        value  = getreg(self.ip_mmap, reg.fifo2_rd_size)
        return(value)
    def get_fifo_waddr(self):
        value  = getreg(self.ip_mmap, reg.fifo2_waddr)
        return(value)