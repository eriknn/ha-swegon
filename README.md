# Home assistant Custom component for Swegon Modbus TCP/IP

## Installation

1. Download using HACS or manually put it in the custom_components folder.
2. Add the integration (Devices and services -> Add integration)
3. Configure the integration via the configure button in the now-added integration.

## Important note

There's a drop-down where you can select many parameters for configuration. This was an attempt to be able to configure a lot of parameters without adding many entities etc. This didn't work out too well I think, as it's difficult to understand what the values are, scaling etc. I still don't think the idea's too bad though, so anyone's very much welcome to improve on this! If we find a good way to do this, it'd be easy to expand the list.
Both ZigBee and Z-Wave has some decent ways to configure devices - ZigBee the best I think. But I don't think it's possible for a custom integration to have a "Configure device" button. I would love that for other integrations as well!

## Hardware

I'm using this to convert from modbus RTU to TCP/IP:     
USR-W610: https://www.aliexpress.com/item/1005005321384583.html?spm=a2g0o.order_list.order_list_main.120.d2c01802wPBgq0

It's been rock solid and with industrial quality. 
It can be powered from the 24VDC output of the ventilation system.
Use an ethernet cable from the SEC/SEM connector, and a screw terminal like this:  
https://www.aliexpress.com/item/33013765148.html?spm=a2g0o.order_list.order_list_main.110.67091802FmEm42  
Connect terminals 1 and 2 to the USR-W610.

## Supported devices

Implemented using the Swegon CASA modbus list (R4-C). This is probably the same for other models as well. We are reading the model name from the device, and as long as we're able to do that we could automatically select a modbus list. Or maybe have a selection for devices in the integration configuration. Let me know if this is needed and we can figure it out!
