# -*- coding: utf-8 -*-
"""
Zybo side: generate TX audio, acquire RX audio, compute 3 correlations,
stream ONE selected correlation window via UDP, and send compact MEAS packet.

Run on Zybo:
  python3 main_zybo.py
"""

import time
import socket
import numpy as np

try:
    import cfg_local as cfg
    print("Loaded cfg_local.py")
except ModuleNotFoundError:
    import cfg as cfg
    print("Loaded cfg.py")

# # use cfg.FS, cfg.PC_IP, ...
# FS = cfg.FS
# PC_IP = cfg.PC_IP


from hw.regBlockC import RegBlock
from hw.audio_peripherals import Audio, HwVersion, Sliders


from dsp.pack import unpack_stereo_int32
from dsp.corr import cyclic_crosscorr_fft, peak_lag_of_fftshifted_corr, slice_around_center
from dsp.gen import Generator

from net.udp_corr import UdpCorrSender
from net.meas import pack_meas

from ui.plot_utils import plot_3_correlations, plot_rx_tx_waveforms




# ---------------- command handling (kept Zybo-local, unchanged logic) ----------------
def make_cmd_socket(bind_ip, cmd_port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((bind_ip, cmd_port))
    s.setblocking(False)
    return s


def parse_and_apply_cmd(msg, state):
    """
    Commands are ASCII like:
      WAVE=SINE | WAVE=AWGN | WAVE=PRBS | WAVE=ZERO | WAVE=CHIRP
      M=64
      N=128
      ALPHA=0.8
      NOISE_STD=0.3
      NHARM=5
      ROLLOFF=1/k   (or 1/k2 or equal)
      SHIFT=-50
      DELAY_COMP=12   (samples, compensates codec/group delay for Tx→Mic lags)
      PLOT=LR | PLOT=TXL | PLOT=TXR
    """
    msg = msg.strip()
    if not msg or "=" not in msg:
        return False

    key, val = msg.split("=", 1)
    key = key.strip().upper()
    val = val.strip()

    try:
        if key == "WAVE":
            val_u = val.upper()
            if val_u in ("SINE", "AWGN", "PRBS", "ZERO", "CHIRP"):
                state["wave"] = val_u
                return True

        elif key == "M":
            state["m"] = float(val)
            return True

        elif key == "N":
            state["n"] = float(val)
            return True

        elif key == "ALPHA":
            state["alpha"] = float(val)
            return True

        elif key == "NOISE_STD":
            state["noise_std"] = float(val)
            return True

        elif key == "NHARM":
            state["nharm"] = int(float(val))
            return True

        elif key == "ROLLOFF":
            if val in ("1/k", "1/k2", "equal"):
                state["rolloff"] = val
                return True

        elif key == "SHIFT":
            state["shift"] = int(float(val))
            return True

        elif key == "DELAY_COMP":
            state["delay_comp"] = int(float(val))
            return True

        elif key == "PLOT":
            val_u = val.upper()
            if val_u in ("LR", "TXL", "TXR"):
                state["plot"] = val_u
                print("received PLOT", val_u)
                return True

    except Exception:
        return False

    return False


# ---------------- hardware init ----------------
def init_hw():
    ip_dict = {"bridge": 0x43C00000, "core": 0x83C10000}

    ip = {}
    for key in ip_dict:
        ip[key] = RegBlock(ip_dict[key], 0x1000)

    shadow_regs = [0] * 34

    # Create peripherals
    sliders = Sliders(ip["core"], shadow_regs, -1)
    print("Sliders = ",sliders.get())

    #get hardware serial number from FPGA id register
    hw_version = HwVersion(ip["core"], shadow_regs)
    print("FPGA Version = ",hw_version.get())

    audio = Audio(ip["core"], shadow_regs)
    audio.audio_select(1)
    audio.fxgen_wavsel(4)
    audio.fifo_enable(0)
    audio.fifo_enable(1)
    audio.line_activate()
    audio.audio_mute(1, 0)
    audio.audio_in_scale(1)
    audio.audio_loop(0)

    wrsize = audio.get_fifo_wrsize()
    print("audio fifo wr size:", wrsize)

    return audio, sliders


# ---------------- waveform application ----------------
def apply_waveform_state(audio, gen, state):
    """This is the main block of apply_waveform_state that creates the transmit buffer:
    It generates a stereo buffer based on the waveform type (SINE, ZERO, etc.)
    and writes it to the TX FIFO.
    The specific waveform types are:
    - SINE: generates a sine wave with multiple harmonics
    - ZERO: creates a stereo buffer of zeros
    - AWGN: generates Gaussian noise
    - PRBS: generates a pseudo-random binary sequence
    - CHIRP: generates a frequency-modulated sine wave
 
    Regenerate TX buffer based on state and push into TX FIFO.
    Also returns txref (mono float32) used for Tx↔Rx correlations.
    """
    #STUDENT_TODO_START: apply audio fifo reset
# HINT
    # Apply audio fifo reset
    # Reset the TX FIFO (FIFO2) to clear any residual audio
    # This ensures a clean start for each waveform
    # 
    
    #STUDENT_TODO_END

    # create default txbuffer of zeros so that incomplete function calls are handled gracefully 
    txbuf = gen.stereo_zero(cfg.FIFOSIZE)

    #STUDENT_TODO_START: create various stereo waveforms for the transmit buffer
# HINT
    # Example sinewave including harmoncs generation
    # This block is the SINE waveform case inside apply_waveform_state:
    # It generates a stereo buffer with multiple harmonics using gen.stereo_sine_harmonics(...), 
    # parameterized by GUI/command state (m, n, nharm, rolloff, amplitude 0.8, seed 42).
    # It then mimics the original behavior by loading only the first m samples 
    # into the Zybo TX FIFO (audio.fifo_send(txbuf[:mN])) instead of the whole FIFO.
    # It measures and prints how long the FIFO load took in microseconds for visibility.
       
    if state["wave"] == "SINE":
        txbuf = gen.stereo_sine_harmonics(
            cfg.FIFOSIZE,
            m=int(state["m"]),
            n=int(state["n"]),
            nharm=int(state["nharm"]),
            harm_rolloff=state["rolloff"],
            amp=0.8,
            seed=42,
        )
        # Specific behavior for SINE waveform: only write m samples
        mN = int(state["m"])
        start = time.perf_counter()
        audio.fifo_send(txbuf[:mN])
        stop = time.perf_counter()
        print(f"time to load tx buffer: {(stop-start)*1e6:.1f} us")

        #Example to create zero data transmit buffer, write all FIFOSIZE samples
        #In the ZERO waveform branch, it sends silence to the DACs:
        #It builds a stereo buffer of zeros with gen.stereo_zero(...) 
        #and writes it to the TX FIFO, so playback is muted for that frame
    elif state["wave"] == "ZERO":
        txbuf = gen.stereo_zero(cfg.FIFOSIZE)
        audio.fifo_send(txbuf)

    # ADD THE OTHER WAVEFORM TYPES AWGN, PRBS, CHIRP HERE
    #elif state["wave"] == "AWGN":

#STUDENT_TODO_END

    """
    This is the tail of apply_waveform_state that prepares the transmit reference:
    unpack_stereo_int32(txbuf) splits the packed stereo buffer into left/right int16 arrays.
    It takes the left channel (txleft_i16), casts it to float32, 
    and stores it as txref — the mono reference used later for Tx↔Rx correlations.
    Returns txref to the caller.
    """
    txleft_i16, _txright_i16 = unpack_stereo_int32(txbuf)
    txref = txleft_i16.astype(np.float32)
    return txref


def main():
    # ---- hardware initialization----
    # STUDENT_TODO_START: instantiate audio/generator to connect to audio interface
# HINT:
    #instantiate the audio interface object and initialize the FPGA interface
    audio,sliders = init_hw()    # initialization of audio interface

    #instantiate the generator object with a seed for AWGN waveform
    gen = Generator(seed=234) 
    
    # STUDENT_TODO_END

    #instantiate the UDP sender object for correlation data
    print("Init UDP sender...")
    # ---- networking ----
    sender = UdpCorrSender(cfg.PC_IP, cfg.CORR_PORT, max_payload=cfg.UDP_MAX_PAYLOAD)
    print("Init command socket...")
    cmd_sock = make_cmd_socket(cfg.CMD_BIND_IP, cfg.CMD_PORT)

    #instantiate the socket object for measurement data
    print("Init measurement socket...")
    meas_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    meas_addr = (cfg.PC_IP, cfg.MEAS_PORT)

    #instantiate the runtime state dictionary
    print("Init runtime state...")
    state = {
        "wave": "SINE",
        "m": 64.0,
        "n": 32.0,
        "alpha": 1.0,
        "noise_std": 0.3,
        "nharm": 1,
        "rolloff": "1/k",
        "shift": 0,
        "delay_comp": getattr(cfg, "DELAY_COMP_SAMPLES", 0),
        "plot": "LR",
    }

    #print the streaming information
    print("Streaming information: CORR to %s:%d, MEAS to %s:%d, listening CMD on UDP *:%d"
          % (cfg.PC_IP, cfg.CORR_PORT, cfg.PC_IP, cfg.MEAS_PORT, cfg.CMD_PORT))

    #apply the waveform state to the audio and generator
    print("Apply waveform state...")
    txref_last = apply_waveform_state(audio, gen, state)

    #initialize the last wave hash for waveform comparison (to update the waveform)
    print("Initialize last wave hash...")
    last_wave_hash = None

    #initialize the frame id for UDP transmission
    print("Initialize frame id...")
    frame_id = 0

    # ---------------- main loop ----------------
    #audio.audio_loop(1)
    print("Start main loop...")
    while True:
        #print(sliders.get())
        #DEBUG OPTION: turn Audio loop ON and OFF with sliders(0)
        # if sliders.get() & 1 :
        #     audio.audio_loop(1)
        # else:
        #     audio.audio_loop(0) 

        t0 = time.perf_counter()

        # -------- handle commands (non-blocking) --------
        any_change = False
        while True:
            try:
                data, src = cmd_sock.recvfrom(1024)
            except BlockingIOError:
                break
            except Exception:
                break

            try:
                msg = data.decode("ascii", errors="ignore")
            except Exception:
                continue

            changed = parse_and_apply_cmd(msg, state)
            if changed:
                any_change = True
                print("CMD from %s: %s -> %s" % (src, msg.strip(), state))

        # Apply waveform only if something relevant changed
        if any_change:
            wave_hash = (state["wave"], state["m"], state["n"], state["alpha"],
                         state["noise_std"], state["nharm"], state["rolloff"])
            if wave_hash != last_wave_hash:
                txref_last = apply_waveform_state(audio, gen, state)
                last_wave_hash = wave_hash
    
        # STUDENT_TODO_START: acquire RX audio
# HINT
        # Trigger the RX FIFO (FIFO2) to acquire audio
        # This starts the audio capture process
        # The time.sleep(0.1) is a placeholder for the actual audio capture time
        # The audio.fifo_receive(cfg.FIFOSIZE) is used to receive the audio data
        # The unpack_stereo_int32(rxbuf) is used to unpack the audio data into left and right channels
        # The rxleft, rxright = unpack_stereo_int32(rxbuf) is used to store the left and right channels
        
        # STUDENT_TODO_END    

        # -------- compute 3 correlations --------
        try:
            corrLR  = cyclic_crosscorr_fft(rxleft, rxright, normalize=True, demean=True).astype(np.float32)
            corrTxL = cyclic_crosscorr_fft(txref,   rxleft, normalize=True, demean=True).astype(np.float32)
            corrTxR = cyclic_crosscorr_fft(txref,   rxright, normalize=True, demean=True).astype(np.float32)
        except Exception:
            # Fallback stub: generate dummy sinc-like correlations if DSP functions fail/missing
            N = cfg.FIFOSIZE
            x = np.linspace(-4, 4, N, dtype=np.float32)
            sinc_stub = np.sinc(x).astype(np.float32)
            corrLR = corrTxL = corrTxR = sinc_stub

        #plot_rx_tx_waveforms(rxright, rxleft, txref, fs=48000.0, nsamples=None, title="RX/TX Waveforms")
        #plot_3_correlations(corrLR, corrTxL, corrTxR, mm_per_sample=None, title="Correlations")


        lag_lr,  peak_lr  = peak_lag_of_fftshifted_corr(corrLR)
        lag_txl, peak_txl = peak_lag_of_fftshifted_corr(corrTxL)
        lag_txr, peak_txr = peak_lag_of_fftshifted_corr(corrTxR)

        # Apply codec/group-delay compensation for Tx→Mic lags (not needed for LR)
        delay_comp = int(state.get("delay_comp", 0))
        lag_txl_adj = lag_txl - delay_comp
        lag_txr_adj = lag_txr - delay_comp
        
        # -------- select which corr window to stream --------
        plot_sel = state.get("plot", "LR")
        if plot_sel == "LR":
            corr_to_send = slice_around_center(corrLR, cfg.WINDOW_LEN)
            which_u8 = 0
        elif plot_sel == "TXL":
            corr_to_send = slice_around_center(corrTxL, cfg.WINDOW_LEN)
            which_u8 = 1
        else:  # "TXR"
            corr_to_send = slice_around_center(corrTxR, cfg.WINDOW_LEN)
            which_u8 = 2

        sender.send_corr(corr_to_send)

        # -------- send MEAS packet --------
        meas_pkt = pack_meas(
            frame_id,
            lag_lr, lag_txl_adj, lag_txr_adj,
            peak_lr, peak_txl, peak_txr,
            which_u8
        )
        meas_sock.sendto(meas_pkt, meas_addr)

        frame_id = (frame_id + 1) & 0xFFFFFFFF

        # -------- maintain ~10 fps --------
        elapsed = time.perf_counter() - t0
        sleep_left = cfg.LOOP_DT - elapsed
        if sleep_left > 0:
            time.sleep(sleep_left)


if __name__ == "__main__":
    main()
