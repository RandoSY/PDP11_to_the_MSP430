/* 01_timer_1khz.c — Candidate source for MSP430G2553, TI/GCC msp430.h.
 * Requires target build, correct board wiring, and physical verification.
 * P1.6/TA0.1 -> Pico GP3; GND common; external supply 3.3V only.
 */
#include <msp430.h>

int main(void) {
    WDTCTL = WDTPW | WDTHOLD;
    if (CALBC1_1MHZ == 0xFF || CALDCO_1MHZ == 0xFF) {
        for (;;) { /* Calibration missing: STOP, don't erase InfoA. */ }
    }
    DCOCTL = 0;
    BCSCTL1 = CALBC1_1MHZ;
    DCOCTL = CALDCO_1MHZ;
    BCSCTL2 &= ~(SELS | DIVS_3); /* DCO source, SMCLK /1 */

    P1DIR |= BIT6;
    P1SEL |= BIT6;
    P1SEL2 &= ~BIT6;
    TA0CCR0 = 499;             /* Counts 0..499: 500 ticks */
    TA0CCR1 = 250;             /* Compare once per timer period */
    TA0CCTL1 = OUTMOD_4;      /* Toggle on CCR1 compare */
    TA0CTL = TASSEL_2 | MC_1 | TACLR; /* SMCLK, up mode */
    for (;;) { __no_operation(); }
}
