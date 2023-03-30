from machine import Pin
import rp2

@rp2.asm_pio(autopush=True, sideset_init=(rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH, rp2.PIO.OUT_HIGH))
def mcp3202():
    wait(1,irq, 4)  .side(0b111)    # CS, CLK, Din

    nop()           .side(0b001)    # Start bit
    in_(null, 1)    .side(0b011)
    in_(null, 1)    .side(0b001)    # SGL bit
    in_(null, 1)    .side(0b011)
    nop()           .side(0b000)    # L/R bit
    nop()           .side(0b010)
    nop()           .side(0b001)    # MSBF bit
    nop()           .side(0b011)
    set(x, 12)           .side(0b001)    # null bit
    label("data_loop0")
    in_(pins, 1)    .side(0b011)
    jmp(x_dec, "data_loop0") .side(0b001)

    wait(1,irq, 4)  .side(0b111)

    push()

class MCP3202:
    def __init__(self, smID = 0):
        self.sm = rp2.StateMachine(smID, mcp3202, freq=1800000, sideset_base=Pin(4), in_base = Pin(2,Pin.IN))
        self.sm.active(1)

    def get(self):
        return self.sm.get()