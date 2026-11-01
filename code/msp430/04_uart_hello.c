/* 04_uart_hello.c — TI/GCC MSP430G2553 at nominal 1MHz, ~9600 8N1.
 * J3: P1.2 TX -> 3.3V adapter RX; GND shared. Do NOT cross power rails.
 * Check actual baud and clock before use as an instrument.
 */
#include <msp430.h>
static void putc_uart(char c) {
    while (!(IFG2 & UCA0TXIFG)) {}
    UCA0TXBUF = (unsigned char)c;
}
static void puts_uart(const char *s) { while (*s) putc_uart(*s++); }
int main(void) {
    WDTCTL = WDTPW | WDTHOLD;
    if (CALBC1_1MHZ == 0xFF || CALDCO_1MHZ == 0xFF) for (;;) {}
    DCOCTL = 0; BCSCTL1 = CALBC1_1MHZ; DCOCTL = CALDCO_1MHZ;
    BCSCTL2 &= ~(SELS | DIVS_3);
    P1SEL |= BIT1 | BIT2; P1SEL2 |= BIT1 | BIT2;
    UCA0CTL1 |= UCSWRST;
    UCA0CTL1 = UCSWRST | UCSSEL_2; /* SMCLK */
    UCA0BR0 = 104; UCA0BR1 = 0; UCA0MCTL = UCBRS0;
    UCA0CTL1 &= ~UCSWRST;
    for (;;) {
        puts_uart("STATUS,HELLO,1MHz_nominal\r\n");
        __delay_cycles(1000000);  /* nominal ~1 sec, CPU-dependent */
    }
}
