$ErrorActionPreference = 'Stop'
$out = Join-Path $env:TEMP ('msp430-host-tests-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $out | Out-Null
try {
  python -m unittest discover -s tests -p 'test_*.py' -v
  if ($LASTEXITCODE -ne 0) { throw 'Python tests failed' }
  gcc -std=c11 -Wall -Wextra -Werror -pedantic -Icode/msp430 tests/test_ds18b20_c.c code/msp430/06_ds18b20_decode.c -o (Join-Path $out 'decode.exe')
  if ($LASTEXITCODE -ne 0) { throw 'Decoder build failed' }
  & (Join-Path $out 'decode.exe')
  if ($LASTEXITCODE -ne 0) { throw 'Decoder test failed' }
  gcc -std=c11 -Wall -Wextra -Werror -pedantic -Icode/msp430 tests/test_sensor_evidence.c code/msp430/12_sensor_evidence.c code/msp430/06_ds18b20_decode.c -o (Join-Path $out 'sensor_evidence.exe')
  if ($LASTEXITCODE -ne 0) { throw 'Sensor evidence build failed' }
  & (Join-Path $out 'sensor_evidence.exe')
  if ($LASTEXITCODE -ne 0) { throw 'Sensor evidence test failed' }
  gcc -std=c11 -Wall -Wextra -Werror -pedantic -Icode/msp430 tests/thermostat_host_test.c -o (Join-Path $out 'thermostat.exe')
  if ($LASTEXITCODE -ne 0) { throw 'Thermostat build failed' }
  & (Join-Path $out 'thermostat.exe')
  if ($LASTEXITCODE -ne 0) { throw 'Thermostat test failed' }
  gcc -std=c11 -Wall -Wextra -Werror -pedantic -Icode/msp430 code/msp430/11_supervisor_demo_HOST.c -o (Join-Path $out 'supervisor.exe')
  if ($LASTEXITCODE -ne 0) { throw 'Supervisor build failed' }
  & (Join-Path $out 'supervisor.exe')
  if ($LASTEXITCODE -ne 0) { throw 'Supervisor failed' }
} finally { Remove-Item -LiteralPath $out -Recurse -Force }
