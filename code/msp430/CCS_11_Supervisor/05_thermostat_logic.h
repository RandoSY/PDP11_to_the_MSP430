/* Platform-independent demonstrator state machine. No mains/load driver.
 * Fractional Celsius value represented as signed 1/16 degree integer.
 */
#ifndef THERMOSTAT_LOGIC_H
#define THERMOSTAT_LOGIC_H
#include <stdint.h>
typedef enum { CONTROL_OFF=0, CONTROL_ON=1, CONTROL_FAULT=2 } control_state_t;
static inline control_state_t control_step(control_state_t old, int16_t temp_x16,
                                            uint8_t sensor_valid) {
    if (!sensor_valid) return CONTROL_FAULT;
    if (temp_x16 >= 30 * 16) return CONTROL_ON;
    if (temp_x16 <= 28 * 16) return CONTROL_OFF;
    if (old == CONTROL_ON) return CONTROL_ON;
    return CONTROL_OFF; /* fail-safe recovery in hysteresis band */
}
#endif
