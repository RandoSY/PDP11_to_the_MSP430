"""DS18B20 scratchpad CRC and signed decoding; HOST ONLY, not sensor I/O."""
def crc8(data):
    crc=0
    for byte in data:
        for _ in range(8):
            mix=(crc ^ byte)&1;crc >>= 1
            if mix:crc ^= 0x8C
            byte >>= 1
    return crc

def decode_scratchpad(data):
    if len(data)!=9:raise ValueError("Expected nine scratchpad bytes")
    if crc8(data[:8])!=data[8]:raise ValueError("1-Wire CRC mismatch")
    resolution=9+((data[4]>>5)&3)
    mask=(0xFFFF << (12-resolution)) & 0xFFFF
    raw=(data[0]|data[1]<<8)&mask
    if raw>=0x8000:raw-=0x10000
    c=raw/16
    return c,c*9/5+32

def synthetic_scratchpad(raw_x16,resolution=12):
    if resolution not in (9,10,11,12):raise ValueError("Resolution must be 9-12")
    raw=raw_x16 & 0xFFFF
    first8=[raw&255,raw>>8,0x4B,0x46,0x1F|((resolution-9)<<5),0xFF,0x0C,0x10]
    return bytes(first8+[crc8(first8)])

if __name__=='__main__':
    for raw in (464,-162):
        data=synthetic_scratchpad(raw)
        print("SYNTHETIC",data.hex(' '),decode_scratchpad(data))
