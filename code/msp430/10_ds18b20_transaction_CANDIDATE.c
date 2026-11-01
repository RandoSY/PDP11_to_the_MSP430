/* DS18B20 single-sensor transaction example, MSP430G2553 (CANDIDATE).
 * NOT verified on MSP430 target. Use only with externally powered DS18B20,
 * one confirmed device, properly configured 3.3 V data pull-up,
 * 1 MHz clock, and scope-confirmed 1-Wire timing from module 09.
 * 1-Wire and UART code are intentionally separate modules.
 */
#include <msp430.h>
#include <stdint.h>
#include "06_ds18b20_decode.h"

/* Implemented in 09_onewire_transport_CANDIDATE.c */
void ow_init(void);
unsigned int ow_reset(void);
void ow_write_byte(uint8_t);
uint8_t ow_read_byte(void);

/* Returns: 0 valid conversion, -1 no presence, -2 CRC failure,
 * -3 null result pointer. It does not establish absolute accuracy.
 * Blocking conversion wait is appropriate only as a teaching baseline.
 * Never call from an interrupt handler or a timing-critical control loop.
 */
int ds18b20_read_single_x16(int16_t *result)
{
    uint8_t scratchpad[9], i;
    if (!result) return -3;
    if (!ow_reset()) return -1;
    ow_write_byte(0xCC);               /* Skip ROM: ONE device only */
    ow_write_byte(0x44);               /* Convert T */
    __delay_cycles(750000UL);          /* Up to 750 ms, nominal 1 MHz */
    if (!ow_reset()) return -1;
    ow_write_byte(0xCC);
    ow_write_byte(0xBE);               /* Read Scratchpad */
    for (i=0; i<9; ++i) scratchpad[i]=ow_read_byte();
    return ds18b20_decode_x16(scratchpad, result);
}
