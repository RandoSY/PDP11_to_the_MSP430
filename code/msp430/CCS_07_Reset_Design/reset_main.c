#include <msp430.h>
void ow_init(void); unsigned int ow_reset(void);
volatile unsigned int trigger, presence;
int main(void) { WDTCTL = WDTPW | WDTHOLD;
    if (CALBC1_1MHZ == 0xFF || CALDCO_1MHZ == 0xFF) { for (;;) {} }
    DCOCTL = 0; BCSCTL1 = CALBC1_1MHZ; DCOCTL = CALDCO_1MHZ;
    BCSCTL2 &= ~(SELS | DIVS_3);
    ow_init();
    for (;;) { if (trigger) { trigger = 0; presence = ow_reset(); } }
}
