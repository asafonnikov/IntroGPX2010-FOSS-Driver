import libevdev, usb.core, usb.util, os

dev = usb.core.find(idVendor=0x08f2, idProduct=0x6811)

while not dev:
    input('Intro GPX2010 not found! Connect tablet and press Enter')
    dev = usb.core.find(idVendor=0x08f2, idProduct=0x6811)

# Pen communating at 1.12.5
ep = dev[0].interfaces()[2].endpoints()[0]
i  = dev[0].interfaces()[2]

if dev.is_kernel_driver_active(2):
    dev.detach_kernel_driver(2)

eaddr = ep.bEndpointAddress
prevData = []

#Initialize

tablet = libevdev.Device()
tablet.name = "Intro GPX2010 Floi's driver"
tablet.enable(libevdev.EV_ABS.ABS_X,
            libevdev.InputAbsInfo(minimum=0, maximum=4095))
tablet.enable(libevdev.EV_ABS.ABS_Y,
            libevdev.InputAbsInfo(minimum=0, maximum=4095))
tablet.enable(libevdev.EV_ABS.ABS_PRESSURE,
               libevdev.InputAbsInfo(minimum=0, maximum=4095))
uinput = tablet.create_uinput_device()
print(f"Initialize as {uinput.devnode} ({uinput.syspath})")

while True:
    try:
        data = dev.read(eaddr, 72)
    except usb.core.USBTimeoutError:
        continue
    x = data[2] + data[3] * 256
    y = data[4] + data[5] * 256
    z = data[6] + data[7] * 256
    # All other, just random data
    uinput.send_events([
                libevdev.InputEvent(libevdev.EV_ABS.ABS_X,
                                    value=x),
                libevdev.InputEvent(libevdev.EV_ABS.ABS_Y,
                                    value=y),
                libevdev.InputEvent(libevdev.EV_ABS.ABS_PRESSURE,
                                    value=z)])
    print(f"X {x}; Y {y}; Z {z}")

