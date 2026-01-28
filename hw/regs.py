buttons               = (0x00,0,3)    # 4 zybo buttons
sliders               = (0x00,4,7)    # 4 zybo sliders
leds                  = (0x01,0,3)    # 4 zybo leds
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
identifier            = (0x05,0,31)   # fpga hardware identifier
fifo_rdata            = (0x06,0,31)   # fifo read data
fifo_rd_stb           = (0x06,0,0)    # fifo read strobe (generated inside fpga on fifo read)
fifo_wdata            = (0x06,0,31)   # fifo write data
fifo_wr_stb           = (0x06,0,0)    # fifo write strobe (generated inside fpga on fifo write)
fifo_wr_size          = (0x07,0,15)   # fifo size for write access
fifo_rd_size          = (0x08,0,15)   # fifo size for read access
buzzer_select         = (0x09,0,1)    # 0 = buzzer controlled by dds   1 = buzzer controlled by register  2 = buzzer morsecode
buzzer_reg            = (0x09,4,4)    # buzzer on/off controlled by register
dma_rate_fcw          = (0x0A,0,29)   # conversion factor = 2**30 / 100e6 = 10.737       fcw = 10737 --> f = 1kHz
dma_rd_en             = (0x0A,30,30)  # enable the dma read transfer
dma_wr_en             = (0x0A,31,31)  # enable the dma write transfer
dma_wrptr             = (0x0B,0,31)   # dma write pointer (tracks dma write bursts)
dma_rdptr             = (0x0C,0,31)   # dma read pointer (tracks dma read bursts)
dma_rd_select         = (0x0D,0,1)    # 00 = audio   others  = TBD
dma_rd_sampling       = (0x0D,3,3)    # 0 = dma_rate_fcw determines sample rate  1 = native audio samples
dma_wr_select         = (0x0D,4,5)    # 00 = audio   others  = dma_testpattern
dma_wr_sampling       = (0x0D,6,6)    # 0 = dma_rate_fcw determines sample rate  1 = native audio samples
dma_testpattern       = (0x0E,0,31)   # testpattern for dma write transfer testing
pmod_o                = (0x0F,0,7)    # 8-bit parallel digital output
pmod_o_select         = (0x0F,8,8)    # 0 = pmod_o   1 =  debug outputs
snd_pulse_period      = (0x11,0,15)   # sounding pulse period in audio samples @48kHz
snd_pulse_length      = (0x11,16,31)  # sounding pulse length in audio samples @48kHz
snd_pulse_repetitions = (0x12,0,7)    # sound pulse repetition number
snd_trig              = (0x12,0,0)    # trigger to send sound pulses
buzzer_fcw            = (0x13,0,26)   # conversion factor = 2**27 / 100e6 = 1.34       fcw = 1342 --> f = 1kHz
sounding_ready        = (0x14,0,0)    # 1= sounding fsm ready for measurement
gpio_o                = (0x15,0,7)    # Digital Outputs
gpio_dir              = (0x15,8,15)   # 0 = output   1 = input  gpio direction
gpio_i                = (0x16,0,7)    # Digital Inputs
light_barrier_1_mux   = (0x17,0,2)    # select light barrier 1 gpio input
light_barrier_2_mux   = (0x17,4,6)    # select light barrier 2 gpio input
speed_trap_en         = (0x17,8,8)    # enable speed trap measurements
speed_trap_guard_time = (0x17,16,31)  # minimum time in usec for light barrier interruption
i2c_luxmeter          = (0x18,0,31)   # luxmeter reading
luxmeter_trigger      = (0x18,0,0)    # start luxmeter
disp_data             = (0x1A,0,31)   # 32-bit BCD coded or binary data for 8 display digits
disp_dp               = (0x1B,0,7)    # 8 decimal points  0 = off  1 = on
disp_blank            = (0x1B,8,15)   # individual  digit blanking  0 = digit ON   1 = digit OFF
dsp_dump              = (0x1C,0,7)    # number of audio samples to be integrated per dump
dsp_scale             = (0x1C,8,10)   # barrell shifter to scale audio signal integration result
dsp_dump_sel          = (0x1C,16,16)  # 0 = use register read to dump   1 = use dsp_dump value to dump
dsp_envelope          = (0x1D,0,31)   # rectified and integrated audio iput signal
dsp_dump_stb          = (0x1D,0,0)    # strobe to dump audio signal
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
