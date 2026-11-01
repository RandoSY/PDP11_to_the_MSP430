#include <msp430.h>
void ow_init(void); void ow_write_bit(unsigned int); unsigned int ow_read_bit(void);
volatile unsigned int trigger, sample;
int main(void) { WDTCTL = WDTPW | WDTHOLD;
    if (CALBC1_1MHZ == 0xFF || CALDCO_1MHZ == 0xFF) { for (;;) {} }
    DCOCTL = 0; BCSCTL1 = CALBC1_1MHZ; DCOCTL = CALDCO_1MHZ;
    BCSCTL2 &= ~(SELS | DIVS_3);
    ow_init();
    for (;;) {
        if (trigger == 1) { trigger = 0; ow_write_bit(1); }
        else if (trigger == 2) { trigger = 0; ow_write_bit(0); }
        else if (trigger == 3) { trigger = 0; sample = ow_read_bit(); }
    }
}
