import time
import uctypes
from dma import DMA

def test_dma():
    dma = DMA(0)
    read_buffer  = bytes(range(256))
    write_buffer = bytearray(256)
    dma.config( 
        read_addr = uctypes.addressof( read_buffer ), 
        write_addr = uctypes.addressof( write_buffer ),
        trans_count = len( read_buffer ), 
        read_inc = True, 
        write_inc = True
    )

    t0 = time.ticks_us()
    dma.enable()
    while( dma.is_busy() ):
        pass
    dma.disable()
    t1 = time.ticks_us()

    print( "dst", write_buffer)
    print( "DMA time [us]: ", t1-t0)
    print( "Transfer speed [B/s]:", len( read_buffer )/((t1-t0)*1e-6) )
    print( "Cycles: ", (t1-t0)*machine.freq() // 1000000)
    print( "@CPU freq:", machine.freq() )

test_dma()

print( "done" )