#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "12_sensor_evidence.h"
#include "06_ds18b20_decode.h"
static uint8_t bytes[17], writes[5];
static unsigned int position, count, resets, fail_reset, waited;
static unsigned int reset_bus(void) { ++resets; return resets != fail_reset; }
static void write_byte(uint8_t b) { writes[count++] = b; }
static uint8_t read_byte(void) { assert(position < sizeof bytes); return bytes[position++]; }
static void wait_conversion(void) { ++waited; }
static void setup(void) {
    const uint8_t scratch[9]={0x50,0x05,0x4b,0x46,0x7f,0xff,0x0c,0x10,0x1c};
    memset(bytes,0,sizeof bytes); bytes[0]=0x28; bytes[1]=1;
    bytes[7]=onewire_crc8(bytes,7); memcpy(bytes+8,scratch,9);
    position=count=resets=fail_reset=waited=0;
}
int main(void) {
    const sensor_bus_t bus={reset_bus,write_byte,read_byte,wait_conversion}; sensor_evidence_t out;
    setup(); assert(sensor_capture(&bus,&out)==0); assert(out.rom_captured && out.scratch_captured);
    assert(out.temperature_x16==1360 && waited==1 && resets==3 && count==5);
    assert(writes[0]==0x33 && writes[1]==0xcc && writes[2]==0x44 && writes[3]==0xcc && writes[4]==0xbe);
    setup(); fail_reset=1; assert(sensor_capture(&bus,&out)==-1 && !out.rom_captured && !out.scratch_captured);
    setup(); bytes[7]^=1; assert(sensor_capture(&bus,&out)==-4 && out.rom_captured && !out.scratch_captured);
    setup(); bytes[0]=0x10; bytes[7]=onewire_crc8(bytes,7); assert(sensor_capture(&bus,&out)==-5);
    setup(); fail_reset=3; assert(sensor_capture(&bus,&out)==-1 && out.rom_captured && !out.scratch_captured);
    setup(); bytes[16]^=1; assert(sensor_capture(&bus,&out)==-2 && out.scratch_captured);
    assert(sensor_capture(0,&out)==-3); return 0;
}
