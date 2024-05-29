"""
Contains all the info necessary for the communication between Mainc Computer (MC) and Laser (L)
The Coherent Vendor ID of the USB laser is
3405

the ProductId is
59

This can be checked with:

import usb.core
devices = usb.core.find(find_all= True)
for device in devices:
    print(f"Vendor ID: ", (device.idVendor), "Product ID: ", (device.idProduct)

"""
import usb.core
import usb.util

VENDOR_ID = hex(3405)
PRODUCT_ID = hex(59)