import config

def myprint(data, verbosity = 0, irc = None):
    if verbosity <= config.LOG_VERBOSITY:
        global logfile
        print(data)
        if irc != None: irc.log(data)
        logfile = open(config.LOG_FILENAME, "a")
        logfile.write(data + "\n")
        logfile.close()

def print_status(address, irc, status1, status2=None):
    status_str = ['Crash ', 'Works ', 'Freeze ']
    fullstatus = "%8x: " % address
    fullstatus += status_str[status1]
    if status2 is not None:
        fullstatus += status_str[status2]
        if (status1 == 2) and (status2 == 0):
            fullstatus += '<-WHOA MOMMA!'
        elif status1 is not status2:
            fullstatus += '<-INTERESTING'
    myprint(fullstatus, 0, irc)
