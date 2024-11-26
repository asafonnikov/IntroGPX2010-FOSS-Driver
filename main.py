import libevdev, usb.core, usb.util, time, os

def handleTablet(dev):
    # Pen communating at 1.12.5
    ep = dev[0].interfaces()[2].endpoints()[0]
    eaddr = ep.bEndpointAddress

    if dev.is_kernel_driver_active(2):
        print("Detaching kernal driver")
        dev.detach_kernel_driver(2)

    tablet = libevdev.Device()
    tablet.name = "Intro GPX2010 Floi's driver"
    tablet.enable(libevdev.EV_ABS.ABS_X,        libevdev.InputAbsInfo(0, 4095))
    tablet.enable(libevdev.EV_ABS.ABS_Y,        libevdev.InputAbsInfo(0, 4095))
    tablet.enable(libevdev.EV_ABS.ABS_PRESSURE, libevdev.InputAbsInfo(0, 2097))
    # When i remove this 'useless' lines, tablet no more emulating
    # So don't remove🙅
    tablet.enable(libevdev.EV_REL.REL_X)
    tablet.enable(libevdev.EV_REL.REL_Y)
    tablet.enable(libevdev.EV_KEY.BTN_LEFT)
    tablet.enable(libevdev.EV_KEY.BTN_RIGHT)

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
                    libevdev.InputEvent(libevdev.EV_ABS.ABS_X, x),
                    libevdev.InputEvent(libevdev.EV_ABS.ABS_Y, y), # Libevdev very lack of documentation
                    libevdev.InputEvent(libevdev.EV_KEY.BTN_LEFT, z), # EV_ABS.ABS_PRESSURE basiclly dont work
                    libevdev.InputEvent(libevdev.EV_SYN.SYN_REPORT, 0)]) # why i dont know🤷‍♂️
        print(f"X {x}; Y {y}; Z {z}")


def main():
    dev = usb.core.find(idVendor=0x08f2, idProduct=0x6811)

    if not dev:
        print('Waiting for tablet')
        while not dev:
            dev = usb.core.find(idVendor=0x08f2, idProduct=0x6811)

    try:
        handleTablet(dev)
    except Exception as e:
        print(e)
        time.sleep(0.1) # Maybe user disconnet tablet which cause I/O error
        main() # Sleep in case that error in code, so stackoverflow was a little late

if __name__ == "__main__":
    if os.geteuid() != 0:
        input("Permission denied! You should run this programm for sudo!\r\nPress Enter to exit")
        exit()
    main()
