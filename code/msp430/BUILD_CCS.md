# Building and debugging with Code Composer Studio

CCS is an alternative to PlatformIO for the MSP-EXP430G2ET and its onboard eZ-FET. The sources have been compiled and linked with TI's MSP430 compiler, but the CCS project setup and physical debug session below have not yet been verified end to end.

See [CCS_PROJECTS.md](CCS_PROJECTS.md) for all eleven ready-made projects. For the quickest start, import the ready-made [`CCS_GPIO_Starter`](CCS_GPIO_Starter/README.md) project. It was generated and successfully built by CCS; target upload and debug remain untested.

1. Install CCS with MSP430 device support, the TI MSP430 compiler and the eZ-FET drivers. Connect the LaunchPad with a USB data cable and verify its power and debug jumpers against the [G2ET user guide](https://www.ti.com/lit/ug/slau772a/slau772a.pdf).
2. Create an MSP430 project targeting **MSP430G2553**, using the TI MSP430 compiler and the TI MSP430 USB debug connection. Select an empty project or a G2553 example project with a device-specific linker command file. Project wizard labels differ between CCS versions.
3. Add or link **one** of `01_timer_1khz.c`, `02_gpio_switch.c`, `03_interrupt_led.c`, or `04_uart_hello.c` to the project. Remove or exclude any generated example source containing another `main`. Ensure the project uses the MSP430G2553 linker command file; do not add another conflicting linker file.
4. Build the project. For a first debug session, use the GPIO example and a Debug configuration. Set a breakpoint at the `P2IN` test. Start debugging with the eZ-FET, then step through and inspect registers. Follow the switch wiring and expected behavior in [BUILD_PLATFORMIO.md](BUILD_PLATFORMIO.md).

Repeat with a separate project or change the selected source to build the other standalone programs. Do not put all four in a single project: each defines `main`. The `08_compare_register_loop.asm` fragment is not a complete program, and `11_supervisor_demo_HOST.c` is a host application.

The sensor files `06_ds18b20_decode.c`, `09_onewire_transport_CANDIDATE.c`, and `10_ds18b20_transaction_CANDIDATE.c` are library modules, not a complete application. They can be compiled and linked with `platformio_sensor_build_check.c` as a build check only. That harness is not a sensor demo and should not be used as one. A working application still needs clock and bus initialization, reporting, wiring and physical timing validation.

On this PC, TI MSP430 compiler 21.6.1.LTS compiled and linked all four standalone examples and the sensor build check against TI's G2553 headers and linker command file. That is a compiler/linker check, not a CCS project import, debugger test or physical measurement. See [TI's CCS project and debug guide](https://software-dl.ti.com/ccs/esd/documents/ccs_getting-started.html) for the applicable CCS version.
