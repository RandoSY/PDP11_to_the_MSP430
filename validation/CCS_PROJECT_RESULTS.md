# CCS project builds — November 1, 2026

CCS 20.4.1 headless project creation and Debug builds succeeded for the ten projects CCS_01_Timer, CCS_03_Interrupt, CCS_04_UART, CCS_05_Thermostat, CCS_06_Decode, CCS_07_Reset_Design, CCS_08_Assembly, CCS_09_OneWire_Slots, CCS_10_Sensor and CCS_11_Supervisor, using TI MSP430 compiler 21.6.1.LTS. The existing CCS_GPIO_Starter was imported and built separately. CCS_08 was reimported and built after its standalone assembly wrapper was corrected.

PlatformIO's five existing build environments also succeeded after adding the CCS folders. No project was uploaded or debugged on physical hardware, and no electrical or timing measurements were performed. The harnesses are explained in each project README.
