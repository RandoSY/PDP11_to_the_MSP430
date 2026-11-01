/* 02_gpio_switch.c — Active-low switch P2.0 controls LED on P1.0.
 * Verify physical polarity; a P1.0 high may or may not light your LED.
 */
#include <msp430.h>
int main(void) {
    WDTCTL = WDTPW | WDTHOLD;
    P1SEL &= ~BIT0; P1SEL2 &= ~BIT0;
    P1DIR |= BIT0; P1OUT &= ~BIT0;
    P2SEL &= ~BIT0; P2SEL2 &= ~BIT0;
    P2DIR &= ~BIT0; P2REN |= BIT0; P2OUT |= BIT0;
    for (;;) {
        if ((P2IN & BIT0) == 0) P1OUT |= BIT0;
        else P1OUT &= ~BIT0;
    }
}
