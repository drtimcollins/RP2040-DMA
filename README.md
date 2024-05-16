*Note: As of December 2023, I would recommend anyone wanting to make use of the RP2040 DMA controller using MicroPython to update to v1.22.0 (or later). The rp2.DMA class is now part of the release and achieves a lot of the functionality that the library in this repository was written for.*

For historical interest, however...

# RP2040 DMA
Micropython library for the RP2040 DMA controller.

To run the examples, copy the 'dma.py' file onto the RP2040 device first.

## Examples
**Ex01_DMASimpleArrayCopy.py** - Just copies bytes from one array to another using DMA.

**Ex02_DMAtoPIOtoLED.py** - Creates a simple PIO to shift bits from the PIO FIFO to the onboard LED (pico board - pin 25). DMA is used to copy data from a bytearray to the PIO output buffer at a rate determined by the PIO clock.

**Ex03_DMAUsingChainTo.py** - Same PIO as Ex02 but uses two DMA controllers with separate buffers configured using the chain_to field to work in 'ping-pong' mode. Each DMA controller automatically triggers the other at the end of its buffer to enable continuous transmission.

**Ex04_DMAtoPIOtoI2S.py** - Uses the ping-pong configuration from Ex03 to stream a 1 kHz sine wave test tone audio to a PIO I2S output.

**Ex05_ADCandI2S.py** - Uses an MCP3202 ADC to input an audio stream and outputs as an I2S stream. Viper-compliant signal processing code can be added to the processBuffer() function.

**Ex05a_ADCandI2S.py** - Same as Ex05_ADCandI2S.py but the I2S format is a non-standard variant in terms of the alignment of the LR clock.
