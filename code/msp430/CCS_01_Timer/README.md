# Timer 1 kHz

This is a self-contained Code Composer Studio project for the MSP-EXP430G2ET / MSP430G2553 and onboard eZ-FET. Import this folder with CCS Import Project, select Debug, build, and start debugging. Debugging programs the target and replaces its current firmware. See the parent `CCS_PROJECTS.md` and TI G2ET guide for setup. Each source file here is a project-local copy; changes do not update the parent examples.

The original timer example drives P1.6 with a nominal 1 kHz signal. Check with a counter or scope and common ground.

For the course's Pico W meter, wiring and first-measurement procedure, see [Meet the Pico W frequency meter](../../../instruments/pico_w_frequency_meter/README.md).

Built with CCS 20.4.1 and TI MSP430 compiler 21.6.1.LTS. Physical upload, debugging and measurement have not been verified.
