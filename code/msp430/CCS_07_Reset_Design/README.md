# 1-Wire reset design

This is a self-contained Code Composer Studio project for the MSP-EXP430G2ET / MSP430G2553 and onboard eZ-FET. Import this folder with CCS Import Project, select Debug, build, and start debugging. Debugging programs the target and replaces its current firmware. See the parent `CCS_PROJECTS.md` and TI G2ET guide for setup. Each source file here is a project-local copy; changes do not update the parent examples.

The design note is not firmware. This project pairs it with the candidate transport and a reset harness: once running, pause, set trigger to 1 and resume, then inspect presence. A presence pulse alone does not validate timing or prove a sensor identity.


**Hardware gate:** This candidate uses P1.7 for open-drain 1-Wire, a verified external pull-up to 3.3 V, a common ground, and (for transactions) one externally powered DS18B20. Confirm the wiring and measure actual reset, presence, write and read-slot timing before relying on results. Breakpoints interrupt timing. The blocking transaction is not suitable for a timing-critical control loop.

Built with CCS 20.4.1 and TI MSP430 compiler 21.6.1.LTS. Physical upload, debugging and measurement have not been verified.
