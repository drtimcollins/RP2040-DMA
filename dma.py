import time

import machine
import uctypes
from micropython import const


class DMA:
    DMA_BASE  = 0x50000000
    
    EN    = const(0x01 << 0)
    HIGH_PRIORITY = const(0x01 << 1)
    INCR_READ = const(0x01 << 4)
    INCR_WRITE= const(0x01 << 5)
    IRQ_QUIET = const(0x01 << 21)
    BUSY      = const(0x01 << 24)
    CH_ABORT   = const(0x50000444)
    SIZE_BYTE = const(0x00 << 2)
    SIZE_HALFWORD = const(0x01 << 2)
    SIZE_WORD = const(0x02 << 2)
    
    DREQ_PIO0_TX0 = const(0x00 << 15)
    DREQ_PIO0_TX1 = const(0x01 << 15)
    DREQ_PIO0_TX2 = const(0x02 << 15)
    DREQ_PIO0_TX3 = const(0x03 << 15)
    DREQ_PIO0_RX0 = const(0x04 << 15)
    DREQ_PIO0_RX1 = const(0x05 << 15)
    DREQ_PIO0_RX2 = const(0x06 << 15)
    DREQ_PIO0_RX3 = const(0x07 << 15)
    DREQ_PIO1_TX0 = const(0x08 << 15)
    DREQ_PIO1_TX1 = const(0x09 << 15)
    DREQ_PIO1_TX2 = const(0x0A << 15)
    DREQ_PIO1_TX3 = const(0x0B << 15)
    DREQ_PIO1_RX0 = const(0x0C << 15)
    DREQ_PIO1_RX1 = const(0x0D << 15)
    DREQ_PIO1_RX2 = const(0x0E << 15)
    DREQ_PIO1_RX3 = const(0x0F << 15)
    DREQ_SPI0_TX = const(0x10 << 15)
    DREQ_SPI0_RX = const(0x11 << 15)
    DREQ_SPI1_TX = const(0x12 << 15)
    DREQ_SPI1_RX = const(0x13 << 15)
    DREQ_UART0_TX = const(0x14 << 15)
    DREQ_UART0_RX = const(0x15 << 15)
    DREQ_UART1_TX = const(0x16 << 15)
    DREQ_UART1_RX = const(0x17 << 15)
    DREQ_PWM_WRAP0 = const(0x18 << 15)
    DREQ_PWM_WRAP1 = const(0x19 << 15)
    DREQ_PWM_WRAP2 = const(0x1A << 15)
    DREQ_PWM_WRAP3 = const(0x1B << 15)
    DREQ_PWM_WRAP4 = const(0x1C << 15)
    DREQ_PWM_WRAP5 = const(0x1D << 15)
    DREQ_PWM_WRAP6 = const(0x1E << 15)
    DREQ_PWM_WRAP7 = const(0x1F << 15)
    DREQ_I2C0_TX = const(0x20 << 15)
    DREQ_I2C0_RX = const(0x21 << 15)
    DREQ_I2C1_TX = const(0x22 << 15)
    DREQ_I2C1_RX = const(0x23 << 15)
    DREQ_ADC = const(0x24 << 15)
    DREQ_XIP_STREAM = const(0x25 << 15)
    DREQ_XIP_SSITX = const(0x26 << 15)
    DREQ_XIP_SSIRX = const(0x27 << 15)
    TREQ_TMR0 = const(0x3B << 15)
    TREQ_TMR1 = const(0x3C << 15)
    TREQ_TMR2 = const(0x3D << 15)
    TREQ_TMR3 = const(0x3E << 15)
    TREQ_PERMANENT= const(0x3F << 15)

    
    def __init__( self, channelNumber ):
        self.channel = channelNumber
        channelOffset = channelNumber * 0x40
        self.READ_ADDR     = DMA.DMA_BASE + 0x00 + channelOffset
        self.WRITE_ADDR    = DMA.DMA_BASE + 0x04 + channelOffset
        self.TRANS_COUNT   = DMA.DMA_BASE + 0x08 + channelOffset
        self.CTRL_TRIG     = DMA.DMA_BASE + 0x0C + channelOffset
        self.AL1_CTRL      = DMA.DMA_BASE + 0x10 + channelOffset
    
    def config( self, *, read_addr, write_addr, trans_count, read_inc, write_inc, treq_sel=-1, chain_to=-1, data_size=0):
        """
        Configure the DMA channel.

        - read_addr : Read address
        - write_addr : Write address
        - trans_count : Transfer count
        - read_inc : Increment read address
        - write_inc : Increment write address
        - treq_sel : Transfer Request signal is selected by treq_sel. If treq_sel is -1, then the channel is permanently enabled.
        - chain_to : Chain to the given channel number. If chain_to is -1, then the channel is not chained.
        - data_size : Data size. 0=byte, 1=halfword, 2=word
        """
        if(chain_to == -1):
            chain_to = self.channel
        if(treq_sel == -1):
            treq_sel = DMA.TREQ_PERMANENT
        machine.mem32[ self.CTRL_TRIG ]   = 0
        machine.mem32[ self.READ_ADDR ]   = read_addr
        machine.mem32[ self.WRITE_ADDR ]  = write_addr
        machine.mem32[ self.TRANS_COUNT ] = trans_count
        ctrl = 0
        if( read_inc ):
            ctrl = DMA.INCR_READ
        if( write_inc ):
            ctrl |= DMA.INCR_WRITE
        machine.mem32[ self.CTRL_TRIG ] = ctrl | (chain_to << 11) | treq_sel | DMA.IRQ_QUIET | data_size

    def enable( self ):
        machine.mem32[ self.CTRL_TRIG ] |= DMA.EN

    def enable_notrigger( self ):
        machine.mem32[ self.AL1_CTRL ] |= DMA.EN
    
    def disable( self ):
        machine.mem32[ self.CTRL_TRIG ] = 0
    
    @staticmethod   
    def abort_all( ):
        machine.mem32[DMA.CH_ABORT]=0xFFFF
        time.sleep(0.1)
        machine.mem32[DMA.CH_ABORT]=0 
    
    def is_busy( self ):
        if( machine.mem32[ self.CTRL_TRIG ] & DMA.BUSY ):
            return True
        else:
            return False

