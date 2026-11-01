import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

MOCK = r'''(() => {
  let controller, pending = '';
  const settings = {type:'status',release:'TEST_USB',deviceName:'Mock Pico',pin_in:14,pin_out:15,gate_ms:250,samples:3,gen_enabled:false,stream:false};
  window.mockCommands = [];
  const respond = (obj) => {
    const data = new TextEncoder().encode('[1] log\r\nUSB_JSON '+JSON.stringify(obj)+'\r\n');
    controller.enqueue(data.slice(0, 9)); controller.enqueue(data.slice(9));
  };
  const port = {
    async open() {
      this.readable = new ReadableStream({start(c) {controller = c;}});
      this.writable = new WritableStream({write(bytes) {
        pending += new TextDecoder().decode(bytes);
        let i;
        while ((i=pending.indexOf('\n'))>=0) {
          const cmd=pending.slice(0,i).trim(); pending=pending.slice(i+1); window.mockCommands.push(cmd);
          if(cmd === 'SET PIN_IN 3') settings.pin_in=3;
          if(cmd === 'SET GATE 1000') settings.gate_ms=1000;
          if(cmd === 'SET SAMPLES 1') settings.samples=1;
          if(cmd === 'IDN?') respond({type:'hello',name:'Mock Pico',release:'TEST_USB'});
          else if(cmd === 'MEASURE') respond({type:'measure',hz:999,pulses:999,elapsed_us:1000000,gate_ms:settings.gate_ms,samples:settings.samples,pin_in:settings.pin_in,gen_enabled:false,source:'manual'});
          else respond(settings);
        }
      }});
    },
    async close() {window.mockClosed = true;}
  };
  Object.defineProperty(navigator, 'serial', {value:{requestPort:async()=>port}, configurable:true});
})();'''

BLE_MOCK = r'''(() => {
  const tx = new EventTarget();
  tx.startNotifications = async () => {};
  tx.notify = (obj) => {
    const data = new TextEncoder().encode(JSON.stringify(obj) + '\n');
    tx.value = new DataView(data.buffer);
    tx.dispatchEvent(new Event('characteristicvaluechanged'));
  };
  const rx = {writeValueWithResponse: async bytes => {
    const cmd = new TextDecoder().decode(bytes).trim();
    if (cmd === 'IDN?') tx.notify({type:'hello',name:'BLE Mock',release:'BLE_TEST'});
    else if (cmd === 'MEASURE') tx.notify({type:'measure',hz:1000,pulses:1000,elapsed_us:1000000,gate_ms:1000,samples:1,pin_in:3,source:'manual'});
    else tx.notify({type:'status',deviceName:'BLE Mock',pin_in:3,pin_out:15,gate_ms:1000,samples:1,gen_enabled:false});
  }};
  const service = {getCharacteristic:async id => id.includes('0002-') ? rx : tx};
  const gatt = {connected:false,async connect(){this.connected=true;return this;}, async getPrimaryService(){return service;},disconnect(){this.connected=false;}};
  const device = Object.assign(new EventTarget(),{name:'BLE Mock',gatt});
  Object.defineProperty(navigator,'bluetooth',{value:{requestDevice:async()=>device},configurable:true});
})();'''

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe', headless=True)
        page = await browser.new_page()
        failures=[]
        page.on('pageerror', lambda exc: failures.append(str(exc)))
        await page.add_init_script(MOCK)
        await page.goto((Path('instruments/pico_w_frequency_meter/dashboard_usb_ble.html').resolve().as_uri()))
        await page.locator('#connectUsbBtn').click()
        await page.wait_for_function("document.querySelector('#connBadge').textContent.includes('USB: Connected')")
        await page.locator('#setupGp3Btn').click()
        await page.wait_for_function("window.mockCommands.includes('SET SAMPLES 1')")
        await page.locator('#measureBtn').click()
        await page.wait_for_function("document.querySelector('#pulses').textContent === '999'")
        assert await page.locator('#pinSummary').inner_text() == 'GP3 / GP15'
        assert await page.locator('#gateSamples').inner_text() == '1000 ms / 1'
        await page.locator('#disconnectBtn').click()
        await page.wait_for_function('window.mockClosed === true')
        assert not failures, failures
        print('Web Serial connect, fragmented input, GP3 setup, measurement and disconnect passed with a mock.')
        ble_page = await browser.new_page()
        await ble_page.add_init_script(BLE_MOCK)
        await ble_page.goto(Path('instruments/pico_w_frequency_meter/dashboard_usb_ble.html').resolve().as_uri())
        await ble_page.locator('#connectBtn').click()
        await ble_page.wait_for_function("document.querySelector('#connBadge').textContent.includes('Bluetooth: Connected')")
        await ble_page.locator('#measureBtn').click()
        await ble_page.wait_for_function("document.querySelector('#pulses').textContent === '1000'")
        await ble_page.locator('#disconnectBtn').click()
        assert await ble_page.locator('#connBadge').inner_text() == 'Disconnected'
        print('Bluetooth connect, notification, measurement and disconnect passed with a mock.')
        await browser.close()
asyncio.run(main())
