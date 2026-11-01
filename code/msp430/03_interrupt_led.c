/* 03_interrupt_led.c — P1.0 toggles every 100ms, nominally.
 * TA1 in up mode from nominal 1MHz SMCLK/4 = 250kHz.
 * This is a distinct firmware target; don't combine with others unreviewed.
 */
#include <msp430.h>
int main(void) {
    WDTCTL = WDTPW | WDTHOLD;
    if (CALBC1_1MHZ == 0xFF || CALDCO_1MHZ == 0xFF) for (;;) {}
    DCOCTL = 0; BCSCTL1 = CALBC1_1MHZ; DCOCTL = CALDCO_1MHZ;
    BCSCTL2 &= ~(SELS | DIVS_3);
    P1SEL &= ~BIT0; P1SEL2 &= ~BIT0;
    P1DIR |= BIT0; P1OUT &= ~BIT0;
    TA1CCR0 = 24999;
    TA1CCTL0 = CCIE;
    TA1CTL = TASSEL_2 | ID_2 | MC_1 | TACLR;
    __bis_SR_register(LPM0_bits | GIE);
    for (;;) {}
}
#pragma vector=TIMER1_A0_VECTOR
__interrupt void timer1_a0_isr(void) {
    P1OUT ^= BIT0;
}
