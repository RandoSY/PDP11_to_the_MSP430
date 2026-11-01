# CCS project index

Each folder is a self-contained project for the MSP-EXP430G2ET and eZ-FET. In CCS, import a project folder, build the Debug configuration, and start debugging. The target configuration uses TI MSP430 USB. Upload replaces the target firmware. The projects contain copies of their sources; changes to one copy do not propagate to others.

| Project | Purpose |
| --- | --- |
| [CCS_01_Timer](CCS_01_Timer/README.md) | Timer 1 kHz (C) |
| [CCS_Day01_Assembly](CCS_Day01_Assembly/README.md) | Original Day One assembly timer |
| [CCS_GPIO_Starter](CCS_GPIO_Starter/README.md) | 02 GPIO switch |
| [CCS_03_Interrupt](CCS_03_Interrupt/README.md) | Timer interrupt LED |
| [CCS_04_UART](CCS_04_UART/README.md) | UART hello |
| [CCS_05_Thermostat](CCS_05_Thermostat/README.md) | Thermostat logic |
| [CCS_06_Decode](CCS_06_Decode/README.md) | DS18B20 decoder |
| [CCS_07_Reset_Design](CCS_07_Reset_Design/README.md) | 1-Wire reset design |
| [CCS_08_Assembly](CCS_08_Assembly/README.md) | Assembly register loop |
| [CCS_09_OneWire_Slots](CCS_09_OneWire_Slots/README.md) | 1-Wire slot experiments |
| [CCS_10_Sensor](CCS_10_Sensor/README.md) | DS18B20 transaction candidate |
| [CCS_11_Supervisor](CCS_11_Supervisor/README.md) | Synthetic supervisor |
| [CCS_12_Integrated_Lab](CCS_12_Integrated_Lab/README.md) | Optional advanced sensor evidence and control candidate |
| [CCS_Optional_Edu_Macros](CCS_Optional_Edu_Macros/README.md) | Optional macro comparison after register-level GPIO |

The 07 design note, 08 assembly fragment, reusable modules, and host-only 11 example require the small harness or adaptation supplied in their projects. Start with the book's direct register-level examples; the macro and integrated projects are optional later exercises. See each README for intended observations and physical test limitations. These projects have built in CCS 20.4.1 with the TI compiler; none has been verified by uploading or observing hardware.

## Where the projects fit the revised textbook

The project numbers follow companion source filenames, **not chapter or laboratory numbers**.

| Textbook work | Relevant CCS project | Scope and remaining work |
| --- | --- | --- |
| Chapter 4 register comparison | `CCS_08_Assembly` | Runs a wrapped version of the register-loop fragment. The separate Day One timer assembly project is `CCS_Day01_Assembly`. |
| Field labs 04–05 and Chapter 5: timer and measurement | `CCS_01_Timer` | The C example and original Day One assembly are available as separate builds. Independent Pico measurements remain to be performed. |
| Chapter 6 / lab 06: GPIO | `CCS_GPIO_Starter` | Supplies the switch and LED example; verify the actual board wiring and record voltages and output states. |
| Chapter 7 / lab 07: interrupts | `CCS_03_Interrupt` | Supplies the timer interrupt example; physical timing and jitter measurements remain to be made. |
| Chapter 8 / lab 08: UART | `CCS_04_UART` | Supplies the hello message; capture a real transcript and check baud and wiring. |
| Chapter 9 / lab 09: 1-Wire | `CCS_07_Reset_Design`, `CCS_09_OneWire_Slots` | Exercises proposed reset and individual slots. Scope captures and timing validation are required before proceeding. |
| Chapter 10 / lab 10: decoding and sensor | `CCS_06_Decode`, `CCS_10_Sensor` | The first uses synthetic data; the second is a candidate transaction. Its simple harness exposes result and status. The optional `CCS_12_Integrated_Lab` adds ROM and raw scratchpad records; conversion completion and the physical evidence gates remain to be verified. |
| Chapter 11 / lab 11: control | `CCS_05_Thermostat`, `CCS_11_Supervisor` | Exercise state logic with debugger-provided or synthetic inputs. The optional `CCS_12_Integrated_Lab` adds sensor acquisition, LED indications and fault injection; a physical fault/output and UART-disconnect demonstration is still required. |
| Chapter 12 / lab 12: publish evidence | Host Python tools and worksheets | CCS projects do not replace the capture, analysis, raw records and report required by this lab. |

The textbook prints an older excerpt of the 1-Wire transport using `__get_SR_register()`. The companion source and CCS copies use `ow_get_sr()` with a legacy PlatformIO compiler compatibility branch. The intended interrupt-state preservation is unchanged, but the printed excerpt is not byte-for-byte identical to the current source. See `TEXTBOOK_ADDENDUM.md` for the printed-listing correction. The revised PDF remains the reading edition; project build success is a later observation and does not establish physical operation.
