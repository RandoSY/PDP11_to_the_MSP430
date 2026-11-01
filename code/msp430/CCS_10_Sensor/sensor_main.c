#include <msp430.h>
#include <stdint.h>
#include "10_ds18b20_transaction_CANDIDATE.h"
void ow_init(void);
volatile unsigned int trigger;
volatile int status = -9;
volatile int16_t temperature_x16;
int main(void) { int16_t reading = 0; WDTCTL = WDTPW | WDTHOLD;
    if (CALBC1_1MHZ == 0xFF || CALDCO_1MHZ == 0xFF) { for (;;) {} }
    DCOCTL = 0; BCSCTL1 = CALBC1_1MHZ; DCOCTL = CALDCO_1MHZ;
    BCSCTL2 &= ~(SELS | DIVS_3);
    ow_init();
    for (;;) { if (trigger) { trigger = 0; status = ds18b20_read_single_x16(&reading); if (status == 0) temperature_x16 = reading; } }
}
