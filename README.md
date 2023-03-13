# RP2040 DMA
 Micropython library for the RP2040 DMA controller

To run the examples, copy the 'dma.py' file onto the RP2040 device first.

## Examples

*Ex01_DMASimpleArrayCopy* - Just copies bytes from one array to another using DMA

*Ex02_DMAtoPIOtoLED* - Creates a simple PIO to shift bits from the PIO FIFO to the onboard LED (pico board - pin 25). DMA is used to copy data from a bytearray to the PIO output buffer at a rate determined by the PIO clock

*Ex03_DMAUsingChainTo* - Same PIO as Ex02 but uses two DMA controllers with separate buffers configured using the chain_to field to work in 'ping-pong' mode. Each DMA controller automatically triggers the other at the end of its buffer to enable continuous transmission.

