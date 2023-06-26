import utime, uctypes
from rp2 import PIO, asm_pio, StateMachine
from machine import Pin, mem32

PIN_DATAIN = 20
PIN_DATAOUT = 18
PIN_MCK = 16
PIN_BCK = PIN_MCK + 1
PIN_LRCK = PIN_DATAOUT + 1

FREQ = 48000
PIO0_BASE      = 0x50200000

@asm_pio(out_init=PIO.OUT_LOW, set_init=(PIO.OUT_LOW, PIO.OUT_LOW), sideset_init=PIO.OUT_LOW)
def Audio_PIO():
    set(pins, 0b00)         .side(0)  [1]
    pull()                  .side(0)  [1]
    push()                  .side(1)  [1]
    set(x, 23)              .side(1)  [1]
    label("bitloopL")
    out(pins, 1)            .side(0)  [1]
    set(y, 6)               .side(0)  [1]
    in_(pins, 1)            .side(1)  [1]
    jmp(x_dec,"bitloopL")   .side(1)  [1]
    label("noploopL")
    set(pins, 0b00)         .side(0)  [1]
    nop()                   .side(0)  [1]
    nop()                   .side(1)  [1]
    jmp(y_dec,"noploopL")   .side(1)  [1]


    set(pins, 0b10)         .side(0)  [1]
    pull()                  .side(0)  [1]
    push()                  .side(1)  [1]
    set(x, 23)              .side(1)  [1]
    label("bitloopR")
    out(pins, 1)            .side(0)  [1]
    set(y, 6)               .side(0)  [1]
    in_(pins, 1)            .side(1)  [1]
    jmp(x_dec,"bitloopR")   .side(1)  [1]
    label("noploopR")
    set(pins, 0b10)         .side(0)  [1]
    nop()                   .side(0)  [1]
    nop()                   .side(1)  [1]
    jmp(y_dec,"noploopR")   .side(1)  [1]

@asm_pio(set_init=PIO.OUT_LOW)
def mclkGenerator():
    set(pins, 0)
    set(pins, 1)

class Audio:
    def __init__(self,smID = 0):
        
        self.PIN_DATAOUT = Pin(PIN_DATAOUT, Pin.OUT)
        self.PIN_DATAIN = Pin(PIN_DATAIN, Pin.IN)
        self.PIN_BCK = Pin(PIN_BCK, Pin.OUT)
        self.PIN_MCK = Pin(PIN_MCK, Pin.OUT)
        self.PIN_LRCK = Pin(PIN_LRCK, Pin.OUT)
        self.smID = smID        

        self.sm = [StateMachine(self.smID), StateMachine(self.smID + 1)]
        self.sm[0].init( Audio_PIO, freq=FREQ * 512, out_base = self.PIN_DATAOUT, set_base = self.PIN_DATAOUT, in_base = self.PIN_DATAIN, sideset_base=self.PIN_BCK )
        self.sm[1].init( mclkGenerator, freq = FREQ * 512, set_base=self.PIN_MCK)

    def active(self, x):
        if(x == True):
            mem32[PIO0_BASE] = mem32[PIO0_BASE] | (0b11 << self.smID)
            print("active")
        else:
            mem32[PIO0_BASE] = mem32[PIO0_BASE] & ~(0b11 << self.smID)
            print("deactive")            
