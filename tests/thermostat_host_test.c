/* Host-built test of decision logic only; no hardware connected. */
#include <assert.h>
#include "../code/msp430/05_thermostat_logic.h"
int main(void) {
    assert(control_step(CONTROL_OFF, 27*16, 1) == CONTROL_OFF);
    assert(control_step(CONTROL_OFF, 29*16, 1) == CONTROL_OFF);
    assert(control_step(CONTROL_OFF, 30*16, 1) == CONTROL_ON);
    assert(control_step(CONTROL_ON, 29*16, 1) == CONTROL_ON);
    assert(control_step(CONTROL_ON, 28*16, 1) == CONTROL_OFF);
    assert(control_step(CONTROL_ON, 35*16, 0) == CONTROL_FAULT);
    assert(control_step(CONTROL_FAULT, 29*16, 1) == CONTROL_OFF);
    return 0;
}
