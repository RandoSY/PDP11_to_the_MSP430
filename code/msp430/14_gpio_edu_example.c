/* Optional macros compared with Chapter 6's register-level GPIO example.
 * Deliberately use P2.0, not edu430.h's P1.3 BUTTON alias. */
#include "edu430.h"
int main(void) {
    WDTCTL = WDTPW | WDTHOLD;
    CLEAR_BITS(P1SEL, BIT0); CLEAR_BITS(P1SEL2, BIT0);
    SET_BITS(P1DIR, BIT0); CLEAR_BITS(P1OUT, BIT0);
    CLEAR_BITS(P2SEL, BIT0); CLEAR_BITS(P2SEL2, BIT0);
    CLEAR_BITS(P2DIR, BIT0); SET_BITS(P2REN, BIT0); SET_BITS(P2OUT, BIT0);
    for (;;) {
        if (BITS_LOW(P2IN, BIT0)) SET_BITS(P1OUT, BIT0);
        else CLEAR_BITS(P1OUT, BIT0);
    }
}
