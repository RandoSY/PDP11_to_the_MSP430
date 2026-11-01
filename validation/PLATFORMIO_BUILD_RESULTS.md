# PlatformIO build results — November 1, 2026

`pio run` built the four standalone MSP430G2553 examples; `pio run -e sensor_build_check` compiled and linked the decoder, transport, and transaction call chain after the legacy mspgcc intrinsic compatibility change. Platform: timsp430 2.4.0, toolchain-timsp430 1.40603.210219 (GCC 4.6.3), Windows. The sensor environment is only a link check, not a functioning sensor program.

`tests/run_host_tests.ps1` passed all 11 Python tests, C decoder and thermostat tests, and the synthetic host supervisor demonstration using native GCC. This does not validate the target firmware timing. No target upload, board operation, 1-Wire measurement, or physical sensor test was performed.
