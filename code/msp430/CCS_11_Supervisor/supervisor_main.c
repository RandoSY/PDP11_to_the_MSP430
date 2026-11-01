#include <msp430.h>
#include <stdint.h>
#include "05_thermostat_logic.h"
volatile control_state_t states[8];
volatile unsigned int finished;
int main(void) {
    const int16_t values[8] = {27*16,29*16,30*16,29*16,29*16,29*16,31*16,28*16};
    const uint8_t valid[8] = {1,1,1,1,0,1,1,1};
    control_state_t state = CONTROL_OFF; unsigned int i;
    WDTCTL = WDTPW | WDTHOLD;
    for (i=0; i<8; ++i) { state=control_step(state, values[i], valid[i]); states[i]=state; }
    finished=1; for (;;) { __no_operation(); }
}
