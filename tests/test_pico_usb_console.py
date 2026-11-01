"""Host tests for USB line handling only, not MicroPython or Pico hardware."""
import ast
import types
import unittest
from pathlib import Path

source = Path(__file__).resolve().parents[1] / 'instruments/pico_w_frequency_meter/main_usb.py'
tree = ast.parse(source.read_text(encoding='utf-8'))
app = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'FreqMeterApp')
method = next(node for node in app.body if isinstance(node, ast.FunctionDef) and node.name == 'process_usb')
module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))

class Input:
    def __init__(self, data): self.data = list(data)
    def read(self, count): return self.data.pop(0) if self.data else ''
class Poll:
    def __init__(self, stream): self.stream = stream
    def poll(self, timeout): return [(1, 1)] if self.stream.data else []
class MockApp:
    def __init__(self, data):
        self.stream = Input(data)
        self.usb_poller = Poll(self.stream)
        self.usb_buffer = ''
        self.usb_discard = False
        self.commands = []
        self.errors = []
    def handle_command(self, value): self.commands.append(value)
    def _send_err(self, value): self.errors.append(value)
    def pump(self):
        namespace = {'sys': types.SimpleNamespace(stdin=self.stream)}
        exec(compile(module, str(source), 'exec'), namespace)
        namespace['process_usb'](self)

class UsbLines(unittest.TestCase):
    def test_crlf_and_incomplete_line(self):
        obj = MockApp('STATUS?\r\nMEAS')
        obj.pump()
        self.assertEqual(obj.commands, ['STATUS?'])
        obj.stream.data.extend('URE\n')
        obj.pump()
        self.assertEqual(obj.commands, ['STATUS?', 'MEASURE'])
    def test_oversize_line_is_discarded(self):
        obj = MockApp('X'*129 + '\nSTATUS?\n')
        while obj.stream.data: obj.pump()
        self.assertEqual(obj.errors, ['USB line too long'])
        self.assertEqual(obj.commands, ['STATUS?'])

if __name__ == '__main__': unittest.main()
