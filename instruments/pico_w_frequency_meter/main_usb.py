# USB command variant of the original BLE meter (candidate, not hardware tested).
# Install this file on the Pico as main.py; preserve the original first.
# Release: FREQ_METER_DASH_R3
#
# Dashboard-compatible Pico / Pico W MicroPython frequency meter
# - PIO edge counter on GP14 by default
# - Optional PWM generator on GP15 by default
# - Optional BLE Nordic UART Service transport
# - Optional SSD1306 OLED
# - Serial debug always enabled
#
# Existing dashboard compatibility:
#   Commands: IDN?, STATUS?, MEASURE, STREAM ON/OFF, SET ..., GEN ..., SAVE, FACTORY, HELP, PING
#   JSON TX messages: hello, status, measure, ack, error, pong, help, rx, log
#
# Self-test jumper:
#   GP15 -> GP14
#
# Optional OLED wiring:
#   VCC -> 3V3
#   GND -> GND
#   SDA -> GP0
#   SCL -> GP1
#
# Notes:
# - 3.3V logic only on the frequency input pin.
# - BLE requires a BLE-capable board/firmware build.
# - OLED is fully optional.

from machine import Pin, PWM, I2C
import rp2
import time
import sys
import select
import micropython
from micropython import const

micropython.alloc_emergency_exception_buf(100)

try:
    import ujson as json
except ImportError:
    import json

try:
    import bluetooth
    HAVE_BLE = True
except ImportError:
    HAVE_BLE = False

try:
    import ssd1306
    HAVE_SSD1306 = True
except ImportError:
    HAVE_SSD1306 = False

try:
    import struct
except ImportError:
    struct = None


# -------------------------------------------------
# Release / config defaults
# -------------------------------------------------
RELEASE = "FREQ_METER_DASH_R3_USB1"
CONFIG_FILE = "freqmeter_cfg.json"

DEFAULTS = {
    "pin_in": 14,
    "pin_out": 15,
    "gate_ms": 250,
    "samples": 3,
    "stream": False,
    "stream_ms": 1000,
    "gen_enabled": False,
    "gen_hz": 1000,
    "gen_duty_pct": 50,
    "oled_i2c_id": 0,
    "oled_sda": 0,
    "oled_scl": 1,
    "oled_addr": 0x3C,
    "oled_w": 128,
    "oled_h": 64,
    "ble_name": "PicoFreq",
}

# Conservative bounds
MIN_GATE_MS = 10
MAX_GATE_MS = 5000
MIN_STREAM_MS = 100
MAX_STREAM_MS = 10000
MIN_SAMPLES = 1
MAX_SAMPLES = 32
MIN_PIN = 0
MAX_PIN = 28
MIN_GEN_HZ = 1
MAX_GEN_HZ = 200000
MIN_DUTY = 1
MAX_DUTY = 99


# -------------------------------------------------
# Serial debug
# -------------------------------------------------
def serial_log(msg):
    try:
        print("[{:>8}] {}".format(time.ticks_ms(), msg))
    except Exception:
        print(msg)


# -------------------------------------------------
# Persistence
# -------------------------------------------------
def load_config():
    cfg = dict(DEFAULTS)
    try:
        with open(CONFIG_FILE, "r") as f:
            loaded = json.loads(f.read())
        if isinstance(loaded, dict):
            cfg.update(loaded)
            serial_log("Loaded config from {}".format(CONFIG_FILE))
    except OSError:
        serial_log("No saved config; using defaults.")
    except Exception as e:
        serial_log("Config load error: {}".format(e))
    return cfg


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        f.write(json.dumps(cfg))
    serial_log("Saved config to {}".format(CONFIG_FILE))


def delete_config():
    try:
        import os
        os.remove(CONFIG_FILE)
        serial_log("Deleted {}".format(CONFIG_FILE))
    except OSError:
        pass


# -------------------------------------------------
# PIO edge counter
# -------------------------------------------------
@rp2.asm_pio()
def edge_counter():
    mov(x, invert(null))
    wrap_target()
    label("count_loop")
    wait(0, pin, 0)
    wait(1, pin, 0)
    jmp(x_dec, "count_loop")
    wrap()


class PIOFrequencyMeter:
    def __init__(self, sm_id=0, pin_num=14):
        self.sm_id = sm_id
        self.pin_num = pin_num
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self.sm = rp2.StateMachine(
            sm_id,
            edge_counter,
            freq=125_000_000,
            in_base=self.pin
        )
        self.sm.active(0)

    def deinit(self):
        try:
            self.sm.active(0)
        except Exception:
            pass

    def measure_once(self, gate_ms=250):
        self.sm.active(0)
        self.sm.restart()

        t0 = time.ticks_us()
        self.sm.active(1)
        time.sleep_ms(int(gate_ms))
        self.sm.active(0)
        t1 = time.ticks_us()

        self.sm.exec("mov(isr, x)")
        self.sm.exec("push()")
        remaining = self.sm.get()

        pulses = (0xFFFFFFFF - remaining) & 0xFFFFFFFF
        elapsed_us = time.ticks_diff(t1, t0)
        hz = 0.0
        if elapsed_us > 0:
            hz = pulses * 1_000_000 / elapsed_us

        return {
            "hz": hz,
            "pulses": pulses,
            "elapsed_us": elapsed_us,
            "gate_ms": int(gate_ms),
        }

    def measure_avg(self, samples=3, gate_ms=250):
        samples = max(1, int(samples))
        total = 0.0
        last = None
        for _ in range(samples):
            last = self.measure_once(gate_ms=gate_ms)
            total += last["hz"]

        if last is None:
            last = {"hz": 0.0, "pulses": 0, "elapsed_us": 0, "gate_ms": int(gate_ms)}

        last["hz_avg"] = total / samples
        last["samples"] = samples
        return last


# -------------------------------------------------
# PWM generator
# -------------------------------------------------
class TestSignal:
    def __init__(self, pin_num=15):
        self.pin_num = pin_num
        self.pin = Pin(pin_num, Pin.OUT)
        self.pwm = PWM(self.pin)
        self.hz = 1000
        self.duty_pct = 50
        self.enabled = False
        self.stop()

    def _duty_u16_from_pct(self, pct):
        pct = max(MIN_DUTY, min(MAX_DUTY, int(pct)))
        return int((pct * 65535) / 100)

    def set(self, hz, duty_pct=50):
        hz = max(MIN_GEN_HZ, min(MAX_GEN_HZ, int(hz)))
        duty_pct = max(MIN_DUTY, min(MAX_DUTY, int(duty_pct)))
        self.pwm.freq(hz)
        self.pwm.duty_u16(self._duty_u16_from_pct(duty_pct))
        self.hz = hz
        self.duty_pct = duty_pct
        self.enabled = True

    def stop(self):
        try:
            self.pwm.duty_u16(0)
        except Exception:
            pass
        try:
            self.pin.value(0)
        except Exception:
            pass
        self.enabled = False

    def deinit(self):
        try:
            self.stop()
        except Exception:
            pass
        try:
            self.pwm.deinit()
        except Exception:
            pass


# -------------------------------------------------
# Optional OLED
# -------------------------------------------------
class OptionalOLED:
    def __init__(self, cfg):
        self.cfg = cfg
        self.enabled = False
        self.i2c = None
        self.oled = None

        if not HAVE_SSD1306:
            serial_log("OLED disabled: ssd1306 module not installed.")
            return

        try:
            self.i2c = I2C(
                cfg["oled_i2c_id"],
                sda=Pin(cfg["oled_sda"]),
                scl=Pin(cfg["oled_scl"]),
                freq=100_000
            )
            addrs = self.i2c.scan()
            serial_log("OLED I2C scan: {}".format([hex(a) for a in addrs]))

            if cfg["oled_addr"] not in addrs:
                serial_log("OLED not found at {}; continuing without display.".format(hex(cfg["oled_addr"])))
                return

            self.oled = ssd1306.SSD1306_I2C(
                cfg["oled_w"],
                cfg["oled_h"],
                self.i2c,
                addr=cfg["oled_addr"]
            )
            self.enabled = True
            self.splash()
        except Exception as e:
            serial_log("OLED init soft fail: {}".format(e))
            self.enabled = False
            self.oled = None

    def _disable(self, why):
        serial_log("OLED disabled: {}".format(why))
        self.enabled = False
        self.oled = None

    def splash(self):
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            self.oled.text("PIO FREQ METER", 0, 0)
            self.oled.text("DASH COMPAT", 0, 16)
            self.oled.text("IN  GP{}".format(self.cfg["pin_in"])[:16], 0, 32)
            self.oled.text("OUT GP{}".format(self.cfg["pin_out"])[:16], 0, 48)
            self.oled.show()
        except Exception as e:
            self._disable(e)

    def show_freq(self, hz, gate_ms, mode, gen_enabled, gen_hz):
        if not self.enabled:
            return
        try:
            self.oled.fill(0)
            self.oled.text(str(mode)[:16], 0, 0)

            if hz >= 1_000_000:
                line = "{:.3f}MHz".format(hz / 1_000_000.0)
            elif hz >= 1000:
                line = "{:.3f}kHz".format(hz / 1000.0)
            else:
                line = "{:.2f}Hz".format(hz)
            self.oled.text(line[:16], 0, 18)
            self.oled.text("Gate:{}ms".format(gate_ms)[:16], 0, 34)

            if gen_enabled:
                if gen_hz >= 1000:
                    g = "Gen:{:.1f}k".format(gen_hz / 1000.0)
                else:
                    g = "Gen:{}Hz".format(int(gen_hz))
            else:
                g = "Gen:OFF"
            self.oled.text(g[:16], 0, 48)
            self.oled.show()
        except Exception as e:
            self._disable(e)


# -------------------------------------------------
# BLE NUS transport
# -------------------------------------------------
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x03)
_ADV_TYPE_UUID32_COMPLETE = const(0x05)
_ADV_TYPE_UUID128_COMPLETE = const(0x07)

if HAVE_BLE:
    _UART_SERVICE_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
    _UART_RX_UUID = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")  # write to peripheral
    _UART_TX_UUID = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")  # notify from peripheral
    _UART_TX = (_UART_TX_UUID, _FLAG_READ | _FLAG_NOTIFY)
    _UART_RX = (_UART_RX_UUID, _FLAG_WRITE)
    _UART_SERVICE = (_UART_SERVICE_UUID, (_UART_TX, _UART_RX))


def advertising_payload(name=None, services=None):
    payload = bytearray()

    def append(adv_type, value):
        payload.extend((len(value) + 1, adv_type))
        payload.extend(value)

    append(_ADV_TYPE_FLAGS, b"\x06")

    if name:
        n = name.encode() if isinstance(name, str) else name
        append(_ADV_TYPE_NAME, n[:16])

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                append(_ADV_TYPE_UUID128_COMPLETE, b)

    return payload


class OptionalBLEUART:
    def __init__(self, name):
        self.name = name
        self.enabled = False
        self.ble = None
        self.tx_handle = None
        self.rx_handle = None
        self.connections = set()
        self.pending_cmds = []
        self.pending_events = []

        if not HAVE_BLE:
            serial_log("BLE disabled: bluetooth module not available.")
            return

        try:
            self.ble = bluetooth.BLE()
            self.ble.active(True)

            try:
                self.ble.config(rxbuf=1024)
            except Exception:
                pass

            try:
                self.ble.config(gap_name=name)
            except Exception:
                pass

            self.ble.irq(self._irq)
            ((self.tx_handle, self.rx_handle),) = self.ble.gatts_register_services((_UART_SERVICE,))
            self.ble.gatts_write(self.rx_handle, b"")
            self._advertise()
            self.enabled = True
            serial_log("BLE enabled; advertising '{}'".format(name))
        except Exception as e:
            serial_log("BLE init soft fail: {}".format(e))
            self.enabled = False
            self.ble = None

    def _advertise(self):
        if not self.ble:
            return
        try:
            adv = advertising_payload(name=self.name, services=[_UART_SERVICE_UUID])
            self.ble.gap_advertise(250_000, adv_data=adv)
        except Exception as e:
            serial_log("BLE advertise fail: {}".format(e))

    def _irq(self, event, data):
        try:
            if event == _IRQ_CENTRAL_CONNECT:
                conn_handle, addr_type, addr = data
                self.connections.add(conn_handle)
                self.pending_events.append(("connect", conn_handle, bytes(addr)))
            elif event == _IRQ_CENTRAL_DISCONNECT:
                conn_handle, addr_type, addr = data
                self.connections.discard(conn_handle)
                self.pending_events.append(("disconnect", conn_handle, bytes(addr)))
                self._advertise()
            elif event == _IRQ_GATTS_WRITE:
                conn_handle, attr_handle = data
                if attr_handle == self.rx_handle:
                    raw = self.ble.gatts_read(self.rx_handle)
                    if raw:
                        raw = raw.replace(b"\r", b"\n")
                        for part in raw.split(b"\n"):
                            part = part.strip()
                            if part:
                                try:
                                    self.pending_cmds.append(part.decode())
                                except Exception:
                                    self.pending_cmds.append(str(part))
        except Exception:
            pass

    def poll(self):
        events = self.pending_events
        cmds = self.pending_cmds
        self.pending_events = []
        self.pending_cmds = []
        return events, cmds

    def send_line(self, text):
        if not self.enabled or not self.connections:
            return

        if not isinstance(text, str):
            text = str(text)

        data = (text + "\n").encode()
        for i in range(0, len(data), 20):
            chunk = data[i:i + 20]
            dead = []
            for conn in self.connections:
                try:
                    self.ble.gatts_notify(conn, self.tx_handle, chunk)
                except Exception as e:
                    serial_log("BLE notify fail conn {}: {}".format(conn, e))
                    dead.append(conn)
            for conn in dead:
                self.connections.discard(conn)

    def send_json(self, obj):
        try:
            line = json.dumps(obj)
        except Exception as e:
            serial_log("JSON encode fail: {}".format(e))
            return
        self.send_line(line)

    def connection_count(self):
        return len(self.connections)


# -------------------------------------------------
# App
# -------------------------------------------------
class FreqMeterApp:
    def __init__(self):
        self.cfg = load_config()
        self.oled = OptionalOLED(self.cfg)
        self.ble = OptionalBLEUART(self.cfg["ble_name"])
        self.meter = None
        self.gen = None
        self.last_measure_ts = 0
        self.usb_buffer = ""
        self.usb_discard = False
        self.usb_poller = select.poll()
        self.usb_poller.register(sys.stdin, select.POLLIN)
        self._init_hardware()

        serial_log("Startup {}".format(RELEASE))
        serial_log("Input pin GP{} | Output pin GP{}".format(self.cfg["pin_in"], self.cfg["pin_out"]))
        serial_log("BLE {} | OLED {}".format(
            "ENABLED" if self.ble.enabled else "DISABLED",
            "ENABLED" if self.oled.enabled else "DISABLED"
        ))

    def _init_hardware(self):
        self._init_meter(self.cfg["pin_in"])
        self._init_generator(self.cfg["pin_out"])
        if self.cfg["gen_enabled"]:
            self.gen.set(self.cfg["gen_hz"], self.cfg["gen_duty_pct"])
        else:
            self.gen.stop()

    def _init_meter(self, pin_in):
        try:
            if self.meter:
                self.meter.deinit()
        except Exception:
            pass
        self.meter = PIOFrequencyMeter(sm_id=0, pin_num=pin_in)
        self.cfg["pin_in"] = pin_in
        serial_log("Meter input set to GP{}".format(pin_in))

    def _init_generator(self, pin_out):
        try:
            if self.gen:
                self.gen.deinit()
        except Exception:
            pass
        self.gen = TestSignal(pin_num=pin_out)
        self.cfg["pin_out"] = pin_out
        serial_log("Generator output set to GP{}".format(pin_out))

    def _send_json(self, obj):
        self.ble.send_json(obj)
        print("USB_JSON " + json.dumps(obj))

    def _send_ack(self, msg):
        serial_log("ACK: {}".format(msg))
        self._send_json({"type": "ack", "msg": msg})

    def _send_err(self, msg):
        serial_log("ERR: {}".format(msg))
        self._send_json({"type": "error", "msg": msg})

    def _send_log(self, msg):
        serial_log(msg)
        self._send_json({"type": "log", "msg": msg})

    def _send_rx_echo(self, line):
        self._send_json({"type": "rx", "line": line})

    def _hello(self):
        self._send_json({
            "type": "hello",
            "name": self.cfg["ble_name"],
            "release": RELEASE,
        })

    def _status_obj(self):
        return {
            "type": "status",
            "release": RELEASE,
            "deviceName": self.cfg["ble_name"],
            "pin_in": self.cfg["pin_in"],
            "pin_out": self.cfg["pin_out"],
            "gate_ms": self.cfg["gate_ms"],
            "samples": self.cfg["samples"],
            "stream": self.cfg["stream"],
            "stream_ms": self.cfg["stream_ms"],
            "gen_enabled": self.cfg["gen_enabled"],
            "gen_hz": self.cfg["gen_hz"],
            "gen_duty_pct": self.cfg["gen_duty_pct"],
        }

    def _send_status(self):
        obj = self._status_obj()
        self._send_json(obj)
        serial_log("STATUS sent: {}".format(obj))

    def _measure(self, source="manual"):
        stats = self.meter.measure_avg(
            samples=self.cfg["samples"],
            gate_ms=self.cfg["gate_ms"]
        )
        hz = stats["hz_avg"]

        msg = {
            "type": "measure",
            "hz": hz,
            "pulses": stats["pulses"],
            "elapsed_us": stats["elapsed_us"],
            "gate_ms": self.cfg["gate_ms"],
            "samples": self.cfg["samples"],
            "pin_in": self.cfg["pin_in"],
            "pin_out": self.cfg["pin_out"],
            "gen_enabled": self.cfg["gen_enabled"],
            "gen_hz": self.cfg["gen_hz"],
            "gen_duty_pct": self.cfg["gen_duty_pct"],
            "source": source,
            "release": RELEASE,
        }

        serial_log(
            "MEASURE src={} hz={:.3f} pulses={} elapsed_us={} gate_ms={} samples={} gen={} {}Hz @ {}%".format(
                source,
                hz,
                stats["pulses"],
                stats["elapsed_us"],
                self.cfg["gate_ms"],
                self.cfg["samples"],
                self.cfg["gen_enabled"],
                self.cfg["gen_hz"],
                self.cfg["gen_duty_pct"],
            )
        )

        self._send_json(msg)
        self.last_measure_ts = time.ticks_ms()

        self.oled.show_freq(
            hz=hz,
            gate_ms=self.cfg["gate_ms"],
            mode="STREAM" if source == "stream" else "READY",
            gen_enabled=self.cfg["gen_enabled"],
            gen_hz=self.cfg["gen_hz"]
        )

    def _apply_gen_state(self):
        if self.cfg["gen_enabled"]:
            self.gen.set(self.cfg["gen_hz"], self.cfg["gen_duty_pct"])
        else:
            self.gen.stop()

    def _set_pin_in(self, pin_num):
        pin_num = int(pin_num)
        if pin_num < MIN_PIN or pin_num > MAX_PIN:
            raise ValueError("PIN_IN out of range")
        self._init_meter(pin_num)

    def _set_pin_out(self, pin_num):
        pin_num = int(pin_num)
        if pin_num < MIN_PIN or pin_num > MAX_PIN:
            raise ValueError("PIN_OUT out of range")
        current_enabled = self.cfg["gen_enabled"]
        current_hz = self.cfg["gen_hz"]
        current_duty = self.cfg["gen_duty_pct"]
        self._init_generator(pin_num)
        if current_enabled:
            self.gen.set(current_hz, current_duty)

    def process_ble(self):
        if not self.ble.enabled:
            return

        events, cmds = self.ble.poll()

        for ev in events:
            kind, conn, addr = ev
            if kind == "connect":
                serial_log("BLE connect conn={}".format(conn))
                self._hello()
                self._send_status()
            elif kind == "disconnect":
                serial_log("BLE disconnect conn={}".format(conn))

        for cmd in cmds:
            self.handle_command(cmd)

    def process_usb(self):
        # Consume only available input; incomplete lines never block the meter.
        for _ in range(64):
            if not self.usb_poller.poll(0):
                break
            ch = sys.stdin.read(1)
            if not ch:
                break
            if ch in ("\r", "\n"):
                if self.usb_discard:
                    self._send_err("USB line too long")
                elif self.usb_buffer:
                    self.handle_command(self.usb_buffer)
                self.usb_buffer = ""
                self.usb_discard = False
            elif not self.usb_discard:
                if len(self.usb_buffer) >= 128:
                    self.usb_buffer = ""
                    self.usb_discard = True
                else:
                    self.usb_buffer += ch

    def handle_command(self, line):
        cmd = line.strip()
        if not cmd:
            return

        serial_log("CMD <= {}".format(cmd))
        self._send_rx_echo(cmd)

        up = cmd.upper()

        try:
            if up == "IDN?":
                self._hello()

            elif up == "STATUS?":
                self._send_status()

            elif up == "MEASURE":
                self._measure(source="manual")

            elif up == "PING":
                self._send_json({"type": "pong", "ms": time.ticks_ms()})

            elif up == "HELP":
                self._send_json({
                    "type": "help",
                    "commands": [
                        "IDN?",
                        "STATUS?",
                        "MEASURE",
                        "PING",
                        "HELP",
                        "STREAM ON",
                        "STREAM OFF",
                        "SET STREAM_MS <ms>",
                        "SET GATE <ms>",
                        "SET SAMPLES <n>",
                        "SET PIN_IN <gpio>",
                        "SET PIN_OUT <gpio>",
                        "GEN SET <hz> <duty_pct>",
                        "GEN ON",
                        "GEN OFF",
                        "SAVE",
                        "FACTORY",
                    ]
                })

            elif up == "STREAM ON":
                self.cfg["stream"] = True
                self._send_ack("stream on")
                self._send_status()

            elif up == "STREAM OFF":
                self.cfg["stream"] = False
                self._send_ack("stream off")
                self._send_status()

            elif up == "GEN ON":
                self.cfg["gen_enabled"] = True
                self._apply_gen_state()
                self._send_ack("generator on")
                self._send_status()

            elif up == "GEN OFF":
                self.cfg["gen_enabled"] = False
                self._apply_gen_state()
                self._send_ack("generator off")
                self._send_status()

            elif up == "SAVE":
                save_config(self.cfg)
                self._send_ack("saved")

            elif up == "FACTORY":
                delete_config()
                self.cfg = dict(DEFAULTS)
                self._init_hardware()
                self._send_ack("factory reset")
                self._send_status()

            else:
                parts = cmd.split()

                if len(parts) >= 3 and parts[0].upper() == "SET":
                    key = parts[1].upper()
                    value = parts[2]

                    if key == "GATE":
                        v = max(MIN_GATE_MS, min(MAX_GATE_MS, int(float(value))))
                        self.cfg["gate_ms"] = v
                        self._send_ack("gate_ms={}".format(v))
                        self._send_status()

                    elif key == "SAMPLES":
                        v = max(MIN_SAMPLES, min(MAX_SAMPLES, int(value)))
                        self.cfg["samples"] = v
                        self._send_ack("samples={}".format(v))
                        self._send_status()

                    elif key == "STREAM_MS":
                        v = max(MIN_STREAM_MS, min(MAX_STREAM_MS, int(float(value))))
                        self.cfg["stream_ms"] = v
                        self._send_ack("stream_ms={}".format(v))
                        self._send_status()

                    elif key == "PIN_IN":
                        self._set_pin_in(int(value))
                        self._send_ack("pin_in={}".format(self.cfg["pin_in"]))
                        self._send_status()

                    elif key == "PIN_OUT":
                        self._set_pin_out(int(value))
                        self._send_ack("pin_out={}".format(self.cfg["pin_out"]))
                        self._send_status()

                    else:
                        self._send_err("unknown SET key")

                elif len(parts) >= 4 and parts[0].upper() == "GEN" and parts[1].upper() == "SET":
                    hz = max(MIN_GEN_HZ, min(MAX_GEN_HZ, int(float(parts[2]))))
                    duty = max(MIN_DUTY, min(MAX_DUTY, int(float(parts[3]))))
                    self.cfg["gen_hz"] = hz
                    self.cfg["gen_duty_pct"] = duty
                    if self.cfg["gen_enabled"]:
                        self.gen.set(hz, duty)
                    self._send_ack("gen set {}Hz {}%".format(hz, duty))
                    self._send_status()

                else:
                    self._send_err("unknown command")

        except Exception as e:
            self._send_err(str(e))

    def run(self):
        next_stream = time.ticks_add(time.ticks_ms(), self.cfg["stream_ms"])

        while True:
            self.process_ble()
            self.process_usb()

            if self.cfg["stream"]:
                if time.ticks_diff(time.ticks_ms(), next_stream) >= 0:
                    self._measure(source="stream")
                    next_stream = time.ticks_add(time.ticks_ms(), self.cfg["stream_ms"])
            else:
                next_stream = time.ticks_add(time.ticks_ms(), self.cfg["stream_ms"])

            time.sleep_ms(20)


def main():
    app = FreqMeterApp()
    app.run()


try:
    main()
except KeyboardInterrupt:
    serial_log("Stopped by user.")
except Exception as e:
    serial_log("Fatal error: {}".format(e))
    raise
