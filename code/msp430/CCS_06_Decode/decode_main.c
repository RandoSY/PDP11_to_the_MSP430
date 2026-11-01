#include <msp430.h>
#include <stdint.h>
#include "06_ds18b20_decode.h"
volatile int16_t result_x16;
volatile int decode_status;
int main(void) {
    const uint8_t sample[9] = {0x50,0x05,0x4B,0x46,0x7F,0xFF,0x0C,0x10,0x1C};
    int16_t reading = 0;
    WDTCTL = WDTPW | WDTHOLD;
    decode_status = ds18b20_decode_x16(sample, &reading); result_x16 = reading;
    for (;;) { __no_operation(); }
}
