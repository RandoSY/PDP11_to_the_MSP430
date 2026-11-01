#ifndef DS18B20_DECODE_H
#define DS18B20_DECODE_H
#include <stdint.h>
uint8_t onewire_crc8(const uint8_t *bytes, uint8_t len);
int ds18b20_decode_x16(const uint8_t scratchpad[9], int16_t *out_x16);
#endif
