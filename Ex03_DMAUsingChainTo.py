from machine import Pin
import rp2, time, uctypes
from dma import DMA

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
#    print("DMA0: ",hex(machine.mem32[ dma[0].CHx_CTRL_TRIG ]))
#    print("Count 0: ", machine.mem32[ dma[0].CHx_TRANS_COUNT ])    
#    print("DMA1: ",hex(machine.mem32[ dma[1].CHx_CTRL_TRIG ]))
#    print("Count 1: ", machine.mem32[ dma[1].CHx_TRANS_COUNT ])
        if(not dma[0].is_busy()):
            machine.mem32[dma[0].READ_ADDR] = uctypes.addressof( buf0 )
        if(not dma[1].is_busy()):
            machine.mem32[dma[1].READ_ADDR] = uctypes.addressof( buf1 )
        pass
#        time.sleep(.05)
    
except (KeyboardInterrupt, Exception) as e:    
    dma[0].disable()
    dma[1].disable()
    time.sleep(0.1)
    sm.put(0)
    time.sleep(0.1)
    sm.active(0)
