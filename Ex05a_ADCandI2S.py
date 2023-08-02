# Inputs a mono audio signal from channel 0 of an MCP3202
# Sends signal to one channel of the I2S output
# Needs dma.py and MCP3203mono.py copied onto the micropython device

import machine
import rp2
import uctypes
from dma import DMA
from machine import Pin
from MCP3202mono import MCP3202
from rp2 import PIO, asm_pio

PIN_DATA = 18
PIN_BCK = 16
PIN_LRCK = PIN_BCK + 1
FREQ = 44100
gp = Pin(25, Pin.OUT)

BUFFERSIZE = const(2000)

# "Non-standard" I2S format
@asm_pio(out_init=PIO.OUT_LOW, sideset_init=(PIO.OUT_LOW, PIO.OUT_LOW), autopull=True)
def Audio_PIO():
    set(x, 14)            .side(0b01)
    irq(4)                .side(0b01)
    
    label("bitloop1")         
    out(pins, 1)          .side(0b10)   [1]
    jmp(x_dec,"bitloop1") .side(0b11)   [1]
    out(pins, 1)          .side(0b10)   [1]
    set(x, 14)            .side(0b11)
    irq(4)                .side(0b11)
        
    label("bitloop0")  
    out(pins, 1)          .side(0b00)   [1]
    jmp(x_dec,"bitloop0") .side(0b01)   [1] 
    out(pins, 1)          .side(0b00)   [1]
          
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
        self.sm.init( Audio_PIO, freq=FREQ * 128, out_base = self.PIN_DATA, sideset_base=self.PIN_BCK )
 
print("Starting")

tx0 = bytearray(BUFFERSIZE << 1)
tx1 = bytearray(BUFFERSIZE << 1)
rx0 = bytearray(BUFFERSIZE)
rx1 = bytearray(BUFFERSIZE)

i2s = Audio()

DMA.abort_all()

PIO0_BASE      = 0x50200000
PIO0_BASE_TXF0 = PIO0_BASE + 0x10
PIO0_BASE_RXF1 = PIO0_BASE + 0x24

dma = [DMA(0), DMA(1), DMA(2), DMA(3)]
dma[0].config( 
    read_addr = uctypes.addressof( tx0 ), 
    write_addr = PIO0_BASE_TXF0,
    trans_count = len( tx0 ) // 4, 
    read_inc = True, 
    write_inc = False, 
    data_size = DMA.SIZE_WORD,
    treq_sel = DMA.DREQ_PIO0_TX0,
    chain_to = 1
)
dma[1].config( 
    read_addr = uctypes.addressof( tx1 ), 
    write_addr = PIO0_BASE_TXF0,
    trans_count = len( tx1 ) // 4, 
    read_inc = True, 
    write_inc = False,
    data_size = DMA.SIZE_WORD,
    treq_sel = DMA.DREQ_PIO0_TX0,
    chain_to = 0
)
dma[2].config( 
    read_addr = PIO0_BASE_RXF1, 
    write_addr = uctypes.addressof( rx0 ),
    trans_count = len( rx0 ) // 2, 
    read_inc = False, 
    write_inc = True, 
    data_size = DMA.SIZE_HALFWORD,
    treq_sel = DMA.DREQ_PIO0_RX1,
    chain_to = 3
)
dma[3].config( 
    read_addr = PIO0_BASE_RXF1, 
    write_addr = uctypes.addressof( rx1 ),
    trans_count = len( rx1 ) // 2, 
    read_inc = False, 
    write_inc = True, 
    data_size = DMA.SIZE_HALFWORD,
    treq_sel = DMA.DREQ_PIO0_RX1,
    chain_to = 2
)
i2s.sm.active(1)
adc = MCP3202(1)
dma[0].enable()
dma[1].enable_notrigger()
dma[2].enable()
dma[3].enable_notrigger()
print("Set-up complete")

# Using viper for speed
@micropython.viper    
def processBuffer(rx, tx):
    rxP = ptr16(uctypes.addressof(rx))
    txP = ptr16(uctypes.addressof(tx))
    for n in range(int(len(rx)) >> 1):
        txP[n << 1] = (rxP[n] - 0x0800) * 20	# Removes DC offset and applies a gain of 20 
        
nextBuffer = 1
try:
    while(True):
        if(nextBuffer == 0 and not dma[0].is_busy() and not dma[2].is_busy()):
            gp.high()
            machine.mem32[dma[0].READ_ADDR] = uctypes.addressof( tx0 )
            machine.mem32[dma[2].WRITE_ADDR] = uctypes.addressof( rx0 )            
            processBuffer(rx0, tx0)
            nextBuffer = 1
            gp.low()            
        if(nextBuffer == 1 and not dma[1].is_busy() and not dma[3].is_busy()):
            gp.high()
            machine.mem32[dma[1].READ_ADDR] = uctypes.addressof( tx1 )
            machine.mem32[dma[3].WRITE_ADDR] = uctypes.addressof( rx1 )
            processBuffer(rx1, tx1)
            nextBuffer = 0
            gp.low()
           

except (KeyboardInterrupt, Exception) as e:
    print("caught exception {} {}".format(type(e).__name__, e))
    i2s.sm.active(0)
    gp.low()







