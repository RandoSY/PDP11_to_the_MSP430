/* Educational lab integration, not industrial or safety-qualified control.
 * 1-Wire timings and all GPIO/UART behavior require bench verification. */
#include <msp430.h>
#include <stdint.h>
#include "05_thermostat_logic.h"
#include "12_sensor_evidence.h"
#include "06_ds18b20_decode.h"
void ow_init(void);
unsigned int ow_reset(void);
void ow_write_byte(uint8_t);
uint8_t ow_read_byte(void);
static void conversion_wait(void) { __delay_cycles(750000UL); }
static const sensor_bus_t bus = {ow_reset, ow_write_byte, ow_read_byte, conversion_wait};
static sensor_evidence_t evidence;
volatile uint8_t inject_fault = 0; /* 1: corrupt CRC; 2: stale */
volatile int sample_status = -9;
volatile control_state_t control_state = CONTROL_FAULT;
volatile unsigned int sample_number = 0;
static void tx(char c) { while (!(IFG2 & UCA0TXIFG)) {} UCA0TXBUF=(unsigned char)c; }
static void text(const char *s) { while (*s) tx(*s++); }
static void hex8(uint8_t v) { const char *h="0123456789ABCDEF"; tx(h[v >> 4]); tx(h[v & 15]); }
static void hex16(uint16_t v) { hex8((uint8_t)(v >> 8)); hex8((uint8_t)v); }
static void uart_init(void) {
    P1SEL |= BIT1|BIT2; P1SEL2 |= BIT1|BIT2;
    UCA0CTL1=UCSWRST|UCSSEL_2; UCA0BR0=104; UCA0BR1=0; UCA0MCTL=UCBRS0; UCA0CTL1 &= ~UCSWRST;
}
static void outputs(control_state_t state) {
    if (state==CONTROL_ON) P1OUT |= BIT0; else P1OUT &= ~BIT0;
    if (state==CONTROL_FAULT) P1OUT |= BIT6; else P1OUT &= ~BIT6;
}
static void report(void) {
    uint8_t i;
    text("SEQ_HEX="); hex16(sample_number); text(",STATUS=");
    if (sample_status<0) { tx('-'); tx((char)('0'-sample_status)); } else tx('0');
    text(",STATE="); tx((char)('0'+control_state));
    text(",X16_HEX="); hex16((uint16_t)evidence.temperature_x16);
    text(",ROM="); if (evidence.rom_captured) for(i=0;i<8;++i) hex8(evidence.rom[i]); else text("NA");
    text(",SCRATCH="); if (evidence.scratch_captured) for(i=0;i<9;++i) hex8(evidence.scratchpad[i]); else text("NA");
    text(",INJECT="); tx((char)('0'+inject_fault)); text("\r\n");
}
int main(void) {
    int16_t discarded;
    WDTCTL=WDTPW|WDTHOLD;
    P1SEL &= ~(BIT0|BIT6); P1SEL2 &= ~(BIT0|BIT6);
    P1OUT &= ~(BIT0|BIT6); P1DIR |= BIT0|BIT6;
    outputs(CONTROL_FAULT);
    if (CALBC1_1MHZ==0xff || CALDCO_1MHZ==0xff) for (;;) {}
    DCOCTL=0; BCSCTL1=CALBC1_1MHZ; DCOCTL=CALDCO_1MHZ;
    BCSCTL2 &= ~(SELS|DIVS_3); uart_init(); ow_init();
    for (;;) {
        ++sample_number;
        if (inject_fault == 2) {
            evidence.rom_captured=0; evidence.scratch_captured=0;
            evidence.temperature_x16=0; sample_status=-6; /* stale, not acquired */
        } else {
            sample_status=sensor_capture(&bus,&evidence);
            if (inject_fault==1 && evidence.scratch_captured) {
                evidence.scratchpad[8] ^= 1u;
                sample_status=ds18b20_decode_x16(evidence.scratchpad,&discarded);
            }
        }
        control_state=control_step(control_state,evidence.temperature_x16,(uint8_t)(sample_status==0));
        outputs(control_state); /* before telemetry; no PC command affects control */
        report();
        __delay_cycles(250000UL); /* nominal spacing, not a timestamp */
    }
}
