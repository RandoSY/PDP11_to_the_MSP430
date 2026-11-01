#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m unittest discover -s tests -p 'test_*.py' -v
out="$(mktemp -d)"; trap 'rm -rf "$out"' EXIT
cc -std=c11 -Wall -Wextra -Werror -pedantic -Icode/msp430 tests/test_ds18b20_c.c code/msp430/06_ds18b20_decode.c -o "$out/decode"
"$out/decode"
cc -std=c11 -Wall -Wextra -Werror -pedantic -Icode/msp430 tests/test_sensor_evidence.c code/msp430/12_sensor_evidence.c code/msp430/06_ds18b20_decode.c -o "$out/sensor_evidence"
"$out/sensor_evidence"
cc -std=c11 -Wall -Wextra -Werror -pedantic -Icode/msp430 tests/thermostat_host_test.c -o "$out/thermostat"
"$out/thermostat"
cc -std=c11 -Wall -Wextra -Werror -pedantic -Icode/msp430 code/msp430/11_supervisor_demo_HOST.c -o "$out/supervisor"
"$out/supervisor"
printf '\nHOST TESTS PASSED. Target compilation and physical timing not tested.\n'
