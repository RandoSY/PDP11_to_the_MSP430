#include "12_sensor_evidence.h"
#include "06_ds18b20_decode.h"
int sensor_capture(const sensor_bus_t *bus, sensor_evidence_t *out)
{
    uint8_t i;
    if (!bus || !out || !bus->reset || !bus->write_byte ||
        !bus->read_byte || !bus->wait_conversion) return -3;
    out->rom_captured = 0; out->scratch_captured = 0;
    out->temperature_x16 = 0;
    for (i=0; i<8; ++i) out->rom[i]=0;
    for (i=0; i<9; ++i) out->scratchpad[i]=0;
    if (!bus->reset()) return -1;
    bus->write_byte(0x33); /* Read ROM: exactly one device on bus */
    for (i=0; i<8; ++i) out->rom[i]=bus->read_byte();
    out->rom_captured=1;
    if (onewire_crc8(out->rom,7)!=out->rom[7]) return -4;
    if (out->rom[0]!=0x28) return -5;
    if (!bus->reset()) return -1;
    bus->write_byte(0xCC); bus->write_byte(0x44);
    bus->wait_conversion(); /* nominal timing, not proof of completion */
    if (!bus->reset()) return -1;
    bus->write_byte(0xCC); bus->write_byte(0xBE);
    for (i=0; i<9; ++i) out->scratchpad[i]=bus->read_byte();
    out->scratch_captured=1;
    return ds18b20_decode_x16(out->scratchpad,&out->temperature_x16);
}
