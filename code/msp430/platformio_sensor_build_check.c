/* Build/link check only. Do not program as a sensor application. */
#include <msp430.h>
#include <stdint.h>
#include "10_ds18b20_transaction_CANDIDATE.h"
volatile unsigned int build_check_trigger = 0;
volatile int build_check_result;
int main(void)
{
    int16_t reading;
    WDTCTL = WDTPW | WDTHOLD;
    /* Volatile branch retains the complete call graph for the linker. */
    if (build_check_trigger) build_check_result = ds18b20_read_single_x16(&reading);
    for (;;) { __no_operation(); }
}
