/* Host-executable controller demonstration. No MCU I/O; no real loads.
 * Compile: cc -std=c11 -Wall -Wextra -Werror -Icode/msp430 \
 *    code/msp430/11_supervisor_demo_HOST.c -o supervisor_host
 */
#include <stdio.h>
#include <stdint.h>
#include "05_thermostat_logic.h"
int main(void)
{
    const struct {int16_t x16; uint8_t valid;} sequence[] = {
        {27*16,1},{29*16,1},{30*16,1},{29*16,1},
        {29*16,0},{29*16,1},{31*16,1},{28*16,1}
    };
    control_state_t state=CONTROL_OFF;
    size_t i;
    puts("sample,temp_C,valid,state");
    for (i=0; i<sizeof(sequence)/sizeof(sequence[0]); ++i) {
        state=control_step(state,sequence[i].x16,sequence[i].valid);
        printf("%u,%.4f,%u,%d\n",(unsigned)i,
               sequence[i].x16/16.0,(unsigned)sequence[i].valid,(int)state);
    }
    return 0;
}
