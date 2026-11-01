# MSP430G2553 builds with PlatformIO

The reference board is the **MSP-EXP430G2ET LaunchPad with its onboard eZ-FET**. Connect a USB data cable to the eZ-FET connector and check the debug and power jumpers in the [TI board user guide](https://www.ti.com/lit/ug/slau772a/slau772a.pdf). The board connection and debugger have not yet been tested here.

Open the repository folder in VS Code with the PlatformIO extension, or run the commands below in PowerShell from the repository root. PlatformIO uses the existing source files directly; no Energia/Arduino framework is involved. The configuration pins the TI MSP430 platform to 2.4.0. On this machine it selected legacy mspgcc 4.6.3. PlatformIO can install its required packages on first use.

```powershell
pio run                         # build all five environments
pio run -e timer_1khz           # build one example
pio run -e timer_1khz -t upload # program a connected compatible board
```

Choose the corresponding environment in the PlatformIO status bar when using the IDE. The ELF and Intel HEX are in `.pio/build/<environment>/firmware.elf` and `firmware.hex`. Each example is a separate program with its own `main`; do not combine the examples into one image. Upload replaces the target's current firmware. The configuration selects the G2553 device, `tilib` for upload, and `mspdebug` for debugging with eZ-FET and the TI debug stack. The connection has not yet been verified on the board.

## First debugging session

This is a proposed procedure pending a physical test:

1. Connect the G2ET through its eZ-FET USB port. Check its jumpers and power using the TI guide. Install the [TI MSP Debug Stack](https://www.ti.com/tool/MSPDS) if the debugger or drivers are unavailable.
2. In PlatformIO select `gpio_switch` and build it. Set a breakpoint on the input test in `02_gpio_switch.c`.
3. Start the PlatformIO debugger in VS Code. It will attempt to build and load a debug image. Step through the test and inspect `P2IN` and `P1OUT`; use the switch wiring described below.
4. Resume and observe the LED. Breakpoints stop the CPU and change timing; use an instrument with the program running freely to check the timer or 1-Wire timing.

If the probe cannot connect, check the data cable, jumper positions, power, TI debug stack, and competing debugger sessions.

| Environment | Source | What to check on the board |
| --- | --- | --- |
| `timer_1khz` | `01_timer_1khz.c` | P1.6/TA0.1 produces nominal 1 kHz; measure with a suitable instrument and common ground. |
| `gpio_switch` | `02_gpio_switch.c` | Pull P2.0 to ground with a switch and observe P1.0; verify LED polarity. |
| `interrupt_led` | `03_interrupt_led.c` | P1.0 toggles nominally every 100 ms (a 200 ms full cycle). |
| `uart_hello` | `04_uart_hello.c` | P1.2 transmits `STATUS,HELLO,1MHz_nominal` approximately once a second. Use a 3.3 V UART receiver, common ground, 9600 baud, 8N1. |
| `sensor_build_check` | decoder, 1-Wire transport and transaction plus a build harness | Compiles and links the sensor call chain; it is **not** a usable sensor application and should not be uploaded for sensor testing. |

The timer, interrupt, and UART programs use the factory 1 MHz calibration constants and stop if either is erased. `board_build.f_cpu` describes a nominal rate to the build; it does not configure the hardware clock. The sensor modules need an actual application that initializes a calibrated clock and the bus, calls `ow_init` and the transaction function, and reports results. They assume one externally powered DS18B20 and a confirmed pull-up to 3.3 V. Measure 1-Wire timing before relying on readings. The examples are not qualified for mains or industrial control.

The PDP-11 and MSP430 assembly examples are teaching fragments, not PlatformIO firmware. `11_supervisor_demo_HOST.c` is a host program. Test host logic on Windows with `./tests/run_host_tests.ps1` (Python and a native GCC on PATH), or run `bash tests/run_host_tests.sh` in a suitable Unix environment. Neither host tests nor successful target compilation establish physical behavior.

PlatformIO references: [TI MSP430 platform](https://docs.platformio.org/en/latest/platforms/timsp430.html), [G2553 LaunchPad board](https://docs.platformio.org/en/latest/boards/timsp430/lpmsp430g2553.html).
