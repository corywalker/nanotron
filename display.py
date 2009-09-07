import config

def myprint(data, verbosity = 0, irc = None):
    if verbosity <= config.LOG_VERBOSITY:
        global logfile
        print(data)
        if irc != None: irc.log(data)
        logfile = open(config.LOG_FILENAME, "a")
        logfile.write(data + "\n")
        logfile.close()

def print_status(address, irc, status1, status2=3):
    fullstatus = "%8x: " % address
    #Adding first run
    if status1 == 0:
        fullstatus = fullstatus + "Crash!"
        myprint(fullstatus, 0, irc)
        return
    if status1 == 1: fullstatus = fullstatus + "Works! "
    if status1 == 2: fullstatus = fullstatus + "Freeze! "
    #Adding second run
    if status2 == 0: fullstatus = fullstatus + "Crash! <<<========== INTERESTING! =========="
    if status2 == 1:
        if status1 != 1: fullstatus = fullstatus + "Works! <<<========== INTERESTING! =========="
        else: fullstatus = fullstatus + "Works!"
    if status2 == 2:
        if status1 != 2: fullstatus = fullstatus + "Freeze! <<<========== INTERESTING! =========="
        else: fullstatus = fullstatus + "Freeze!"
    #Printing everything
    myprint(fullstatus, 0, irc)
