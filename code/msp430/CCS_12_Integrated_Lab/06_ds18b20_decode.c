/* HOST-TESTED CRC and resolution-aware DS18B20 decoding.
 * Does NOT implement transport, conversion scheduling, or sensor accuracy.
 * Caller must validate fresh conversion and power/temperature conditions.
 */
#include "06_ds18b20_decode.h"
uint8_t onewire_crc8(const uint8_t *bytes,uint8_t len)
{
    uint8_t crc=0,i,j;
    if (!bytes && len) return 0;
    for(i=0;i<len;++i) {
        uint8_t value=bytes[i];
        for(j=0;j<8;++j){
            uint8_t mix=(uint8_t)((crc^value)&1u);
            crc >>= 1;
            if(mix) crc^=0x8Cu;
            value >>= 1;
        }
    }
    return crc;
}
int ds18b20_decode_x16(const uint8_t scratchpad[9],int16_t *out_x16)
{
    uint16_t raw,mask;
    unsigned int resolution;
    if (!scratchpad || !out_x16) return -1;
    if (onewire_crc8(scratchpad,8)!=scratchpad[8]) return -2;
    resolution=9u+((scratchpad[4]>>5)&3u);
    mask=(uint16_t)(0xFFFFu << (12u-resolution));
    raw=((uint16_t)scratchpad[0]|((uint16_t)scratchpad[1]<<8))&mask;
    if (raw&0x8000u) {
        uint16_t magnitude=(uint16_t)(~raw+1u);
        *out_x16=(int16_t)(-(int32_t)magnitude);
    } else *out_x16=(int16_t)raw;
    return 0;
}
