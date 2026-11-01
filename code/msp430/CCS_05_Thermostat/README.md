# Thermostat logic

This is a self-contained Code Composer Studio project for the MSP-EXP430G2ET / MSP430G2553 and onboard eZ-FET. Import this folder with CCS Import Project, select Debug, build, and start debugging. Debugging programs the target and replaces its current firmware. See the parent `CCS_PROJECTS.md` and TI G2ET guide for setup. Each source file here is a project-local copy; changes do not update the parent examples.

A target debugger harness exercises the original header. Change temperature_x16 (degrees C times 16) and sensor_valid in the debugger; observe state: 0 OFF, 1 ON, 2 FAULT. No physical sensor or output is connected.

Built with CCS 20.4.1 and TI MSP430 compiler 21.6.1.LTS. Physical upload, debugging and measurement have not been verified.
