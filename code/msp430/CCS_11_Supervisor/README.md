# Synthetic supervisor

This is a self-contained Code Composer Studio project for the MSP-EXP430G2ET / MSP430G2553 and onboard eZ-FET. Import this folder with CCS Import Project, select Debug, build, and start debugging. Debugging programs the target and replaces its current firmware. See the parent `CCS_PROJECTS.md` and TI G2ET guide for setup. Each source file here is a project-local copy; changes do not update the parent examples.

This target harness adapts the host-only demonstration without printf or floating point. After finished becomes 1, inspect states: 0, 0, 1, 1, 2, 0, 1, 0. It uses synthetic samples and does not control an output.

Built with CCS 20.4.1 and TI MSP430 compiler 21.6.1.LTS. Physical upload, debugging and measurement have not been verified.
