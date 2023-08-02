"""
Creates a simple PIO to shift bits from the PIO FIFO to the onboard LED (pico board - pin 25). 
DMA is used to copy data from a bytearray to the PIO output buffer at a rate determined by the PIO clock.

Same PIO as Ex02 but uses two DMA controllers with separate buffers configured using the chain_to field to work in 'ping-pong' mode. 
Each DMA controller automatically triggers the other at the end of its buffer to enable continuous transmission.
"""

import time

import rp2
import uctypes
from dma import DMA
from machine import Pin, mem32


@rp2.asm_pio(out_init=rp2.PIO.OUT_LOW, autopull=True)
def streamToLed():
    out(pins, 1)
sm = rp2.StateMachine(0, streamToLed, freq=10000,  out_base=Pin(25))
sm.active(1)

DMA.abort_all()

buf0 = bytearray(50)
buf1 = bytearray(50)

for m in range(50):
    buf0[m] = 0xFF
    buf1[m] = 0x02
        
PIO0_BASE      = 0x50200000
PIO0_BASE_TXF0 = PIO0_BASE + 0x10

dma = [DMA(0), DMA(1)]
dma[0].config( 
    read_addr = uctypes.addressof( buf0 ), 
    write_addr = PIO0_BASE_TXF0,
    trans_count = len( buf0 ), 
    read_inc = True, 
    write_inc = False, 
    treq_sel = DMA.DREQ_PIO0_TX0,
    chain_to = 1
)
dma[1].config( 
    read_addr = uctypes.addressof( buf1 ), 
    write_addr = PIO0_BASE_TXF0,
    trans_count = len( buf1 ), 
    read_inc = True, 
    write_inc = False, 
    treq_sel = DMA.DREQ_PIO0_TX0,
    chain_to = 0
)

dma[0].enable()
dma[1].enable_notrigger()

try:
    while(True):
        if(not dma[0].is_busy()):
            mem32[dma[0].READ_ADDR] = uctypes.addressof( buf0 )
        if(not dma[1].is_busy()):
            mem32[dma[1].READ_ADDR] = uctypes.addressof( buf1 )
    
except (KeyboardInterrupt, Exception) as e:    
    dma[0].disable()
    dma[1].disable()
    time.sleep(0.1)
    sm.put(0)
    time.sleep(0.1)
    sm.active(0)
