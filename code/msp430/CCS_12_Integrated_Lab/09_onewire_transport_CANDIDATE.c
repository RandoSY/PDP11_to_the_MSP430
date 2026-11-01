/* MSP430G2553 1-Wire timing demonstration on P1.7.
 * IMPORTANT: Candidate source, not bench-verified. Must measure real slots.
 * Requires independently confirmed external ~4.7k pull-up to target 3.3 V.
 * Timer_A0 is dedicated to this example and therefore cannot simultaneously
 * generate the preceding 1 kHz experiment without redesign.
 * Timing is nominal assuming SMCLK calibrated near 1 MHz.
 */
#include <msp430.h>
#include <stdint.h>
#define OW BIT7

/* PlatformIO's legacy mspgcc calls this intrinsic __read_status_register. */
#if defined(__GNUC__) && (__GNUC__ < 5)
#define ow_get_sr() __read_status_register()
#else
#define ow_get_sr() __get_SR_register()
#endif

static void ow_low(void)
{
    P1OUT &= (unsigned char)~OW;  /* output latch first: never drive high */
    P1DIR |= OW;                  /* pull bus LOW */
}
static void ow_release(void)
{
    P1DIR &= (unsigned char)~OW;  /* input/high impedance; pull-up raises */
}
static void wait_us(unsigned int us)
{
    unsigned int start = TA0R;
    while ((unsigned int)(TA0R - start) < us) { }
}
void ow_init(void)
{
    P1SEL &= (unsigned char)~OW;
    P1SEL2 &= (unsigned char)~OW;
    ow_release();
    /* assumes prior 1 MHz DCO configuration */
    TA0CTL = TASSEL_2 | MC_2 | TACLR; /* continuous timer */
}
/* Returns 1 if presence was observed; 0 for missing/stuck bus.
 * Blocking; interrupts excluded for critical timing, investigate latency.
 */
unsigned int ow_reset(void)
{
    unsigned int present;
    unsigned int gie_was_set = ow_get_sr() & GIE;
    if ((P1IN & OW) == 0) return 0; /* idle must be high */
    __disable_interrupt();
    ow_low();     wait_us(480);
    ow_release(); wait_us(70);
    present = ((P1IN & OW) == 0);
    wait_us(410);
    if (gie_was_set) __enable_interrupt();
    return present;
}
void ow_write_bit(unsigned int bit)
{
    unsigned int gie_was_set = ow_get_sr() & GIE;
    __disable_interrupt();
    ow_low();
    if (bit) { wait_us(6);  ow_release(); wait_us(64); }
    else     { wait_us(60); ow_release(); wait_us(10); }
    if (gie_was_set) __enable_interrupt();
}
unsigned int ow_read_bit(void)
{
    unsigned int bit;
    unsigned int gie_was_set = ow_get_sr() & GIE;
    __disable_interrupt();
    ow_low(); wait_us(6); ow_release();
    wait_us(9); bit = ((P1IN & OW) != 0);
    wait_us(55);
    if (gie_was_set) __enable_interrupt();
    return bit;
}
void ow_write_byte(uint8_t value)
{
    unsigned int i;
    for (i=0; i<8; ++i) { ow_write_bit(value & 1u); value >>= 1; }
}
uint8_t ow_read_byte(void)
{
    unsigned int i;
    uint8_t value=0;
    for (i=0; i<8; ++i) if (ow_read_bit()) value |= (uint8_t)(1u<<i);
    return value;
}
