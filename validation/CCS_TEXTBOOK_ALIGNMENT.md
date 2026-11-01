# CCS and revised textbook alignment — November 1, 2026

Compared the revised PDF's printed listings and field-lab procedures with the companion source and the eleven CCS projects. The project index in `code/msp430/CCS_PROJECTS.md` maps chapters and labs to projects and records the remaining evidence and integration gaps. Each project copy with a matching filename was compared byte-for-byte with the parent source and matched.

The PDF's printed 1-Wire listing precedes the source compatibility change for legacy PlatformIO mspgcc. The source now uses `ow_get_sr()` and a conditional compiler-specific status-register accessor; the printed excerpt still uses `__get_SR_register()`. The separately referenced Day One timer assembly project is not in this archive. Sensor raw-data publication and the integrated sensor/control/output demonstration are also not supplied by the debugger harnesses.

The prior CCS and PlatformIO build results remain build checks; no physical upload, debug session, or hardware observation has been added during this alignment review.

## Later companion updates

The original Day One assembly was located in the prior lab-board package and imported as `CCS_Day01_Assembly`; its source hash matches the original. `CCS_12_Integrated_Lab` adds an optional raw ROM/scratchpad and LED-control candidate, and `CCS_Optional_Edu_Macros` adds an optional macro comparison using a copy of the existing learning-labs `edu430.h`. The original low-level examples remain the primary course material. The revised PDF itself has not been changed: see `code/msp430/TEXTBOOK_ADDENDUM.md` for the source-listing discrepancy.

The three new projects were generated and built with CCS 20.4.1 and TI MSP430 compiler 21.6.1.LTS. Host mock tests verify transaction order, successful decode, missing presence, bad ROM CRC, wrong family, and bad scratchpad CRC. These are software-only checks; no target upload, sensor data, timing measurement, fault-output observation, or physical debugger test was performed.
