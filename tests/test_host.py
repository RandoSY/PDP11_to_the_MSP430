import sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'/'python'))
from cap_analyze import summarize
from ds18b20_math import crc8,decode_scratchpad,synthetic_scratchpad

class Algorithms(unittest.TestCase):
    def test_crc_known(self):self.assertEqual(crc8([0x50,0x05,0x4B,0x46,0x7F,0xFF,0x0C,0x10]),0x1C)
    def test_positive(self):self.assertEqual(decode_scratchpad(synthetic_scratchpad(464))[0],29.0)
    def test_negative(self):self.assertEqual(decode_scratchpad(synthetic_scratchpad(-162))[0],-10.125)
    def test_resolution(self):
        for bits,value in [(9,1.5),(10,1.75),(11,1.875),(12,1.9375)]:
            self.assertEqual(decode_scratchpad(synthetic_scratchpad(31,bits))[0],value)
    def test_bad_crc(self):
        s=bytearray(synthetic_scratchpad(464));s[0]^=1
        with self.assertRaisesRegex(ValueError,'CRC'):decode_scratchpad(s)
    def test_length(self):
        with self.assertRaisesRegex(ValueError,'nine'):decode_scratchpad([])
    def write(self,text):
        self.d=tempfile.TemporaryDirectory();self.addCleanup(self.d.cleanup)
        p=Path(self.d.name)/'m.csv';p.write_text(text);return p
    def test_csv(self):
        x=summarize(self.write('reading_hz\n998\n1000\n1002\n'))
        self.assertEqual((x['n'],x['mean_hz'],x['range_hz']),(3,1000,4))
    def test_csv_blank(self):
        with self.assertRaisesRegex(ValueError,'blank measurement'):
            summarize(self.write('reading_hz,trial\n1000,1\n,2\n'))
    def test_csv_missing_column(self):
        with self.assertRaisesRegex(ValueError,'reading_hz'):summarize(self.write('value\n10\n'))
    def test_csv_nan(self):
        with self.assertRaisesRegex(ValueError,'nonfinite'):summarize(self.write('reading_hz\nnan\n'))
    def test_target(self):
        with self.assertRaisesRegex(ValueError,'Nominal'):summarize(self.write('reading_hz\n12\n'),0)
if __name__=='__main__':unittest.main()
