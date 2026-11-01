/* Host validation ONLY: decoder/CRC, no 1-Wire electrical transport. */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "../code/msp430/06_ds18b20_decode.h"

static void check(uint16_t raw,unsigned resolution,int16_t expected)
{
    uint8_t s[9]={0}; int16_t got=0;
    s[0]=(uint8_t)(raw&0xFF);s[1]=(uint8_t)(raw>>8);
    s[2]=0x4B;s[3]=0x46;s[4]=(uint8_t)(0x1F|((resolution-9)<<5));
    s[5]=0xFF;s[6]=0x0C;s[7]=0x10;
    s[8]=onewire_crc8(s,8);
    assert(ds18b20_decode_x16(s,&got)==0 && got==expected);
    s[3]^=1;assert(ds18b20_decode_x16(s,&got)==-2);
}
int main(void)
{
    const uint8_t known[]={0x50,0x05,0x4B,0x46,0x7F,0xFF,0x0C,0x10};
    assert(onewire_crc8(known,8)==0x1C);
    check(464,12,464);
    check(0xFF5E,12,-162);
    check(31,9,24);
    check(31,10,28);
    check(31,11,30);
    check(31,12,31);
    puts("CRC and DS18B20 decode: HOST-TESTED");
    return 0;
}
