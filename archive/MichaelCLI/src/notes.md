# Essential knowledge for BLE connecting
- `device_dict = await bleakscanner.discover(return_adv=True)` will return a list of discovered devices, `return_adv=True` will include the advertisement data
- `device_list = device_dict.values()` will return a list of discovered devices and their advertisement data
- `device_list[0][0]` contains the following attributes: 
  - `address` is the MAC address of the device
  - `name` is the name of the device
  - `rssi` is the signal strength of the device
  - `metadata` is the advertisement data
- `device_list[0][1]` contains the following attributes:
  - `service_uuids` is a list of service UUIDs
  - `manufacturer_data` is the manufacturer data
  - `service_data` is the service data
  - `local_name` is the local name
  - `tx_power` is the transmission power

# MAC address
- `NIC`: network interface controller
- `OUI`: organizationally unique identifier, first half of the MAC address, assigned by IEEE for manufacturers
- `MAC`: media access control
- 