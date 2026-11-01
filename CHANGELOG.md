# Pico browser USB mode — November 1, 2026

- Added a unified dashboard with Web Serial and Bluetooth modes, a GP3 setup button, and shared measurement controls. Original BLE dashboard remains unchanged.
- Verified browser-side USB and BLE flows with simulated devices; the Pico, USB firmware and actual measurements have not been tested on hardware.

# USB Pico meter option — November 1, 2026

- Added a separate USB-command firmware candidate and USB-first instructions, preserving the original BLE meter.
- Added host tests for USB line parsing; hardware USB, BLE and frequency measurement remain unverified.

# Pico W measurement introduction — November 1, 2026

- Added the existing Pico W frequency-meter firmware and dashboard, plus setup, wiring, capture and analysis guidance for the G2ET timer labs.
- Recorded that the 5,000 ms firmware gate limit differs from the textbook's optional 10,000 ms example. Hardware measurement remains unverified.

# Textbook companion alignment — November 1, 2026

- Recovered the original Day One assembly timer as a separate CCS project, and added optional sensor evidence/control and educational macro comparison projects.
- Kept the core register-level examples as the primary path. Added a PDF addendum explaining the printed 1-Wire listing difference and the boundaries of the later projects.
- Added host mock tests for sensor evidence sequencing; no target or physical results are asserted.

# CCS project collection — November 1, 2026

- Added ten self-contained CCS projects for the remaining numbered MSP430 materials, plus an index and per-project instructions. Non-standalone items use labeled test harnesses or adaptations.
- Built each project with CCS 20.4.1 and confirmed the existing PlatformIO environments still build. Hardware debugging and measurements remain unverified.

# PlatformIO MSP430 build resources — November 1, 2026

- Added separate PlatformIO environments for the four standalone examples and a sensor module build/link check.
- Adapted the 1-Wire status-register intrinsic for PlatformIO legacy mspgcc, and added Windows host-test commands and build guidance.
- All five target builds and host tests passed; no target was programmed or measured.

# Revised illustrated edition companion update — November 1, 2026

- Identified the 144-page Claude-revised PDF as the current reading edition and regenerated the searchable text export from it.
- Compared the revised and previous PDFs: the revised layout incorporates the curriculum figure plates and adds front-matter figure and table lists; companion source listings appear carried forward.
- Corrected archive paths and documented that the supplied editable manuscripts and builder remain prior-edition sources, not a reproducible source for this revision. See `validation/REVISION_AUDIT.md`.

# Final editorial edition changes — October 31, 2026

- Extended industrial history and architecture chapters: UNIBUS, I/O contracts, RSX-11M tasks, interrupt and scheduling constraints, PDP-11/MSP430 encoding comparison.
- Extended instrumentation and control chapters: timing budgets, 1-Wire slot validation, conversion-completion logic, hysteresis fault policy, and reproducible experimental evidence.
- Added dedicated introduction, refreshed final cover/title pages, corrected table of contents, and added final verification appendix.
- Updated Python CSV analysis to reject incomplete recorded measurements and invalid targets; expanded unit-test coverage.
- Updated C and Python DS18B20 decoding to mask the undefined least significant bits at lower sensor resolutions; added C/host regression tests.
- Added single-device, externally powered DS18B20 transaction candidate and separate host-executable supervisor demonstration.
- Maintained target hardware validation gates: no unobserved hardware result is labeled verified.
- Removed duplicate previous-edition files; packaged one coherent reading and editable edition with complete companion files.
