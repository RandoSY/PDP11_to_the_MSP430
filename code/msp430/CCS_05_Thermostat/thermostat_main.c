#include <msp430.h>
#include "05_thermostat_logic.h"
volatile int16_t temperature_x16 = 27 * 16;
volatile uint8_t sensor_valid = 1;
volatile control_state_t state = CONTROL_OFF;
int main(void) { WDTCTL = WDTPW | WDTHOLD; for (;;) { state = control_step(state, temperature_x16, sensor_valid); __no_operation(); } }
