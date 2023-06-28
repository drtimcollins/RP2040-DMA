# Example of synchronous I2S input/output with basic audio signal processing.
# Set-up is for stereo 24-bit operation at 48kHz
# SCLK = 64 x Fs, MCLK = 256 x Fs (target device is CS4272).
# Needs dma.py and audioIO.py copied onto the micropython device
# NOT TESTED YET - I DO NOT KNOW IF THIS WILL WORK!!
# Loopback test connecting DataOut to DataIn is fine but not tried with a real codec yet.

from audioIO import Audio
from dma import DMA
import uctypes, machine

#print(machine.freq())
print("Initialising audio interface...")
i2s = Audio()
DMA.abort_all()

PIO0_BASE      = 0x50200000
PIO0_BASE_TXF0 = PIO0_BASE + 0x10
PIO0_BASE_RXF0 = PIO0_BASE + 0x20

buf = bytes(range(256))
rxbuf = bytearray(256)
print(rxbuf)

i2s.active(True)

#print(machine.mem32[PIO0_BASE + 0xc8])

dma = [DMA(0),DMA(1)]
dma[0].config( 
    read_addr = uctypes.addressof( buf ), 
    write_addr = PIO0_BASE_TXF0,
    trans_count = len( buf ) // 4, 
    read_inc = True, 
    write_inc = False, 
    data_size = DMA.SIZE_WORD,
    treq_sel = DMA.DREQ_PIO0_TX0 
)
dma[1].config( 
    read_addr = PIO0_BASE_RXF0, 
    write_addr = uctypes.addressof( rxbuf ),
    trans_count = len( buf ) // 4, 
    read_inc = False, 
    write_inc = True, 
    data_size = DMA.SIZE_WORD,
    treq_sel = DMA.DREQ_PIO0_RX0 
)
dma[0].enable()
dma[1].enable()

while( dma[0].is_busy() and dma[1].is_busy() ):
    pass
dma[0].disable()
dma[1].disable()
i2s.active(False)
print(rxbuf)



