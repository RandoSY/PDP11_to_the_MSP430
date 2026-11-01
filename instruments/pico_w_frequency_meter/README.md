# Meet the Pico W frequency meter

In the course the MSP430 **creates and controls** a signal; a separate Raspberry Pi Pico W **observes** it. This is the first independent measurement for textbook Chapters 4–5 and field labs 04–05. The Pico is an instrument, not a second MSP430 programmer. The computer is used to program the MSP430, configure the instrument and keep records.

## What is included

- `main.py` — your existing MicroPython meter firmware, release `FREQ_METER_DASH_R3`, copied unchanged from the earlier `MSP430 Minimal/firmware/PICOW_Frequency_METER` package.
- `main_usb.py` — optional candidate variant that adds newline-delimited USB serial commands while retaining BLE. It has not yet been tested on a physical Pico.
- `dashboard_usb_ble.html` — the new browser dashboard with USB and Bluetooth modes.
- `dashboard_compatible_debug_v1_1_0.html` — the original Web Bluetooth dashboard, copied unchanged.
- `../../worksheets/frequency_capture_template.csv` — blank observations for the frequency lab.

The USB route uses a Pico or Pico W with a suitable RP2040 MicroPython build; the optional dashboard requires a **Pico W** with a Bluetooth-capable build. A non-W Pico cannot use the BLE dashboard. The scripts have not been tested on physical hardware in this course archive; the installed MicroPython version and BLE support must be checked on the actual Pico W. The firmware counts frequency; it is not a scope or a microsecond pulse-width capture tool.

## Prepare the Pico W

For USB command control, consult [Raspberry Pi's MicroPython setup](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html), choose the correct build for your board, and use a MicroPython editor such as Thonny to save **`main_usb.py` as `main.py` on the Pico**. Back up any existing Pico `main.py` before replacing it, then reset the Pico. The original bundled `main.py` is preserved as a BLE-only command version: it prints USB debug logs but does not accept the meter commands over USB. The USB variant is a candidate and still needs a physical test. Close Thonny or other serial programs before using a terminal. The optional OLED is not required.

The meter's **factory default input is GP14**, and stored settings can override defaults. Do not assume it is already listening on GP3. The generator and any GP15-to-GP14 self-test jumper must be off/disconnected when observing the MSP430.

## Wire the first measurement

With power off, identify the actual G2ET MSP430G2553 header pins from the [TI board guide](https://www.ti.com/lit/ug/slau772a/slau772a.pdf). Connect:

| G2ET target | Pico W | Purpose |
| --- | --- | --- |
| MSP430 P1.6 / TA0.1 | GP3, physical pin 5 | Nominal 3.3 V timer signal into frequency meter |
| Target GND | Pico GND, for example physical pin 3 | Common signal reference |

Power the G2ET and Pico from their own USB connections; do not tie their 3.3 V rails together. Verify pin numbering and signal voltage before connecting; never feed 5 V into Pico GPIO. The printed textbook's custom-board J2 pin number is for that custom board, not a G2ET header. The G2ET P1.6 LED connection can load the output; check board jumpers and record the setup. Do not connect a driven Pico generator to the MSP430 output.

## Take a reading

1. Import and build `code/msp430/CCS_01_Timer` or the separate `CCS_Day01_Assembly` project. Program the G2ET, then let it run freely; a breakpoint changes CPU behavior. Both examples configure the timer in hardware and expect factory 1 MHz clock calibration.
2. Connect the Pico's USB to the computer. Close Thonny and other serial monitors, then start the web server from the course root:

   ```powershell
   python -m http.server 8000 --bind 127.0.0.1 --directory instruments/pico_w_frequency_meter
   ```

   Open `http://localhost:8000/dashboard_usb_ble.html` in Edge, Chrome, or another browser supporting Web Serial. Click **Connect USB** and select the Pico's serial port. The Pico must be running `main_usb.py` saved on the device as `main.py`; the original BLE firmware cannot accept USB meter commands.
3. Click **Set up GP3 measurement**. This requests the following settings and then reads back status:

   ```text
   STREAM OFF
   GEN OFF
   SET PIN_IN 3
   SET GATE 1000
   SET SAMPLES 1
   STATUS?
   ```

   Confirm the dashboard reports GP3, 1000 ms, one sample and generator OFF. Saved settings may differ. These commands change the running configuration; `SAVE` changes persistent settings and is not needed. If there is no response, verify the USB firmware is running: opening a port alone does not confirm the meter is responding.
4. Click **Measure Once** five times, waiting for each new reading. Save the command log and enter the frequency, pulse count, elapsed microseconds, settings and provenance in the blank worksheet. Do not replace missing observations with predicted values. Use **Disconnect** before closing the page or opening another serial program.
5. Predict 1,000 Hz from `1,000,000 / [2 × (499 + 1)]`. Compare the observations with that prediction and state their spread and limitations. To analyze a completed CSV, run:

   ```powershell
   python code/python/cap_analyze.py path/to/your_completed_capture.csv 1000
   ```

As an alternative to the browser, use a serial terminal. `pio device list` identifies ports; `pio device monitor --port COM5 --baud 115200 --echo` opens an example port, replacing `COM5` with the Pico's port. Send newline-terminated commands such as `STATUS?` and `MEASURE`; responses begin with `USB_JSON`. Close other serial applications first. Ctrl+C exits the PlatformIO monitor.

The Pico PIO counts rising edges and the program calculates frequency from the count and its measured gate duration. A nominal one-second gate has approximately 1 Hz count granularity, before timebase and other errors; decimals on the display do not establish accuracy. Neither board is automatically a traceable reference. With multiple samples, the displayed frequency is an average while the reported pulse count and elapsed time describe the last gate, so use one sample here.

For the follow-up comparison change CCR0 from 499 to 999, rebuild and reprogram, and predict a nominal 500 Hz; retain CCR1 at 250. Record a fresh data set. This firmware limits `SET GATE` to 5,000 ms, so the book's 10,000 ms optional example is not supported by this release.

## If the reading is missing

Check the P1.6 and GP3 identification, common ground, 3.3 V levels, output running, clock calibration, USB COM port, USB variant installation, and `STATUS?`. If the serial port is busy, close other monitors. Reset after copying the USB variant as `main.py`. The USB dashboard and firmware have been tested with software mocks, but not the physical Pico. Check that no active generator or self-test jumper is connected. Confirm firmware and board versions before drawing a conclusion. Use a scope or dedicated timing instrument for 1-Wire slot work.

## Optional Bluetooth dashboard

The original `main.py` uses BLE for commands and emits USB debug logs. To use Bluetooth, keep or install that original file as Pico `main.py` (or try the USB variant, which retains the BLE code). Start the local web server above and open `http://localhost:8000/dashboard_usb_ble.html` in a Web Bluetooth-capable browser. Click **Connect Bluetooth** and select `PicoFreq`. The original page remains available as `dashboard_compatible_debug_v1_1_0.html`. BLE and the USB variant's retained BLE path have not been physically verified in this archive.
