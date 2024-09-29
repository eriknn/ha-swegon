# Home assistant Custom component for Swegon Modbus TCP/IP

## Installation

Download using HACS or manually put it in the custom_components folder.

## Hardware

I'm using this to convert from modbus RTU to TCP/IP:     
USR-W610: https://www.aliexpress.com/item/1005005321384583.html?spm=a2g0o.order_list.order_list_main.120.d2c01802wPBgq0

It's been rock solid and with industrial quality. 
It can be powered from the 24VDC output of the ventilation system.
Use an ethernet cable from the SEC/SEM connector, and a screw terminal like this:  
https://www.aliexpress.com/item/33013765148.html?spm=a2g0o.order_list.order_list_main.110.67091802FmEm42  
Connect terminals 1 and 2 to the USR-W610.

## Supported devices

Implemented using the Swegon CASA modbus list. This is probably the same for other models as well.
