# Companion addendum for the revised textbook

This is a supplement to `From_the_PDP11_to_the_MSP430_Revised_Textbook_CLAUDE.pdf`. The PDF's editable source is not present, so its printed pages and listings have not been rewritten.

- Chapters 4–5 / labs 04–05: the original Day One assembly timer has been recovered from the earlier lab-board package and is now available as `CCS_Day01_Assembly`; compare it with `CCS_01_Timer`. The original assembly's custom-board J2 numbering is not automatically valid for the G2ET.
- The included Pico W meter and dashboard are introduced in `instruments/pico_w_frequency_meter/README.md`. This firmware permits gates up to 5,000 ms; the textbook's optional 10,000 ms gate requires different firmware.
- For a wired start, the meter guide also describes a separate USB-command firmware candidate. The original supplied meter accepts commands over BLE and provides USB debug output; the USB variant is not yet hardware tested.
- Chapter 9 printed listing: current `09_onewire_transport_CANDIDATE.c` uses `ow_get_sr()` with a conditional legacy-mspgcc intrinsic instead of the printed direct `__get_SR_register()`. Both preserve the intended interrupt-state check for their respective toolchains; physical timing still needs verification.
- Chapters 10–11: `CCS_12_Integrated_Lab` adds ROM and raw scratchpad records, state and status telemetry, a classroom indicator and fault-injection hooks. It remains an unverified blocking candidate, not a safety-rated controller or proof of a real conversion. Follow its README and the book's evidence gates.
- Optional Chapter 6 extension: `CCS_Optional_Edu_Macros` compares the prior `edu430.h` bit-operation macros with the book's explicit register operations. Do not substitute its board aliases without checking the actual pin mapping.

All target builds reported here are compiler/linker results, not observations of a physical system.
