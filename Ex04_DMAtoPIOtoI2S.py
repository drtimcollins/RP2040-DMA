import utime, uctypes
from rp2 import PIO, asm_pio
from machine import Pin
from dma import DMA

PIN_DATA = 18
PIN_BCK = 16
PIN_LRCK = PIN_BCK + 1
FREQ = 48000
gp = Pin(25, Pin.OUT)
sine_wave_table = [
  0x8000, 0x90B5, 0xA121, 0xB0FB, 0xC000, 0xCDEB, 0xDA82, 0xE58C, 0xEED9, 0xF641, 0xFBA2, 0xFEE7, 0xFFFF, 0xFEE7
, 0xFBA2, 0xF641, 0xEED9, 0xE58C, 0xDA82, 0xCDEB, 0xC000, 0xB0FB, 0xA121, 0x90B5, 0x8000, 0x6F4B, 0x5EDF, 0x4F05
, 0x4001, 0x3215, 0x257E, 0x1A74, 0x1127, 0x09BF, 0x045E, 0x0119, 0x0001, 0x0119, 0x045E, 0x09BF, 0x1127, 0x1A74
, 0x257E, 0x3215, 0x4000, 0x4F05, 0x5EDF, 0x6F4B]

@asm_pio(out_init=PIO.OUT_LOW, sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW), autopull=True)
def Audio_PIO():
    set(x, 14)            .side(0b11)
    
    label("bitloop1")         
    out(pins, 1)          .side(0b10)
    jmp(x_dec,"bitloop1") .side(0b11)
    out(pins, 1)          .side(0b00)
    set(x, 14)            .side(0b01)
    
    label("bitloop0")  
    out(pins, 1)          .side(0b00)
    jmp(x_dec,"bitloop0") .side(0b01) 
    out(pins, 1)          .side(0b10)
          
class Audio:
    def __init__(self,smID = 0):
        
        self.PIN_DATA = Pin(PIN_DATA)
        self.PIN_BCK = Pin(PIN_BCK)
        self.PIN_LRCK = Pin(PIN_LRCK)
        self.smID = smID
        
        self.PIN_BCK.init(Pin.OUT)
        self.PIN_DATA.init(Pin.OUT)
        self.PIN_LRCK.init(Pin.OUT)
        # Create a state machine with the serial number self.smID
        self.sm= rp2.StateMachine(self.smID) 

        #start state machine
        self.sm.init(
            Audio_PIO,
            freq=FREQ * 64,
            out_base = self.PIN_DATA,
            #set_base=self.PIN_DATA,
            #jmp_pin = self.PIN_DATA,
            sideset_base=self.PIN_BCK,
#             out_shiftdir=PIO.SHIFT_RIGHT
            )
         
        self.buf = bytearray(40 * len(sine_wave_table))
        for i in range(10*len(sine_wave_table)):
            x = (sine_wave_table[i % len(sine_wave_table)] - 0x8000) // 4
            self.buf[(i*4)] = x & 0xFF
            self.buf[(i*4+1)] = (x & 0xFF00 ) >> 8
            self.buf[(i*4+2)] = x & 0xFF
            self.buf[(i*4+3)] = (x & 0xFF00 ) >> 8
        
Pico_Audio = Audio()

DMA.abort_all()

PIO0_BASE      = 0x50200000
PIO0_BASE_TXF0 = PIO0_BASE + 0x10

dma = [DMA(0), DMA(1)]
dma[0].config( 
    read_addr = uctypes.addressof( Pico_Audio.buf ), 
    write_addr = PIO0_BASE_TXF0,
    trans_count = len( Pico_Audio.buf ) // 4, 
    read_inc = True, 
    write_inc = False, 
    data_size = DMA.SIZE_WORD,
    treq_sel = DMA.DREQ_PIO0_TX0,
    chain_to = 1
)
dma[1].config( 
    read_addr = uctypes.addressof( Pico_Audio.buf ), 
    write_addr = PIO0_BASE_TXF0,
    trans_count = len( Pico_Audio.buf ) // 4, 
    read_inc = True, 
    write_inc = False,
    data_size = DMA.SIZE_WORD,
    treq_sel = DMA.DREQ_PIO0_TX0,
    chain_to = 0
)

Pico_Audio.sm.active(1)
dma[0].enable()
dma[1].enable_notrigger()

nextBuffer = 1
try:
    while(True):
        if(nextBuffer == 0 and not dma[0].is_busy()):
            machine.mem32[dma[0].READ_ADDR] = uctypes.addressof( Pico_Audio.buf )
            nextBuffer = 1
            gp.high()
        if(nextBuffer == 1 and not dma[1].is_busy()):
            machine.mem32[dma[1].READ_ADDR] = uctypes.addressof( Pico_Audio.buf )
            nextBuffer = 0
            gp.low()
        pass    

except (KeyboardInterrupt, Exception) as e:
    print("caught exception {} {}".format(type(e).__name__, e))
    Pico_Audio.sm.active(0)
    gp.low()







