#ifndef LAB_SENSOR_EVIDENCE_H
#define LAB_SENSOR_EVIDENCE_H
#include <stdint.h>
typedef struct {
    uint8_t rom[8];
    uint8_t scratchpad[9];
    uint8_t rom_captured;
    uint8_t scratch_captured;
    int16_t temperature_x16;
} sensor_evidence_t;
typedef struct {
    unsigned int (*reset)(void);
    void (*write_byte)(uint8_t);
    uint8_t (*read_byte)(void);
    void (*wait_conversion)(void);
} sensor_bus_t;
/* -1 no presence, -2 scratch CRC, -3 bad argument, -4 ROM CRC,
 * -5 wrong family; 0 valid bytes. One externally powered device only. */
int sensor_capture(const sensor_bus_t *bus, sensor_evidence_t *out);
#endif
