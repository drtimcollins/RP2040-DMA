from rp2 import PIO, asm_pio
from machine import Pin
from dma import DMA
import time, uctypes

@asm_pio(out_init=PIO.OUT_LOW, autopull=True)
def streamToLed():
    out(pins, 1)
    
led = Pin(25)
led.init(Pin.OUT)
sm = rp2.StateMachine(0)
sm.init(streamToLed, freq=2000, out_base = led, set_base=led)

buf = bytearray(300)
for n in range(3):
    for m in range(100):
        if(m < 50):
            buf[n*100+m] = 0xFF
        else:
            buf[n*100+m] = 0x02
        
sm.active(1)
PIO0_BASE      = 0x50200000
PIO0_BASE_TXF0 = PIO0_BASE + 0x10

dma = DMA(0)
dma.config( 
    read_addr = uctypes.addressof( buf ), 
    write_addr = PIO0_BASE_TXF0,
    trans_count = len( buf ), 
    read_inc = True, 
    write_inc = False, 
    treq_sel = DMA.DREQ_PIO0_TX0 
)
dma.enable()
while( dma.is_busy() ):
    pass
dma.disable()
sm.active(0)
