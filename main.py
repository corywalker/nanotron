#!/usr/bin/env python

import struct
import sys
import os
import time
import nanotron
import irc
import dispatcher

#You shouldn't need to change these two
FREEZEPAYLOAD = struct.pack("<8I", 0xe3a030d3, 0xe121f003, 0xe3a03000, 0xe3a025f2,
                                   0xe3a010a5, 0xe5821000, 0xe2511001, 0xeafffffd)
CRASHPAYLOAD = struct.pack("<8I", 0xe3a030d3, 0xe121f003, 0xe3a03000, 0xe3a025f2,
                                  0xe3a010a5, 0xe5821000, 0xe51ff004, 0x41414141)
IPODMODEL = "4G Nano"
versions = "latest" #TODO: find out what this is
                                  
class TronError(Exception):
  pass

try:
    my_nanotron = nanotron.Nanotron()
    dispatcher = dispatcher.Dispatcher(my_nanotron)
    dispatcher.run()
    ircbot = irc.IRCBot(dispatcher)
    ircbot.start("%s, %s" % (IPODMODEL, versions))
    dispatcher.shutdown()
    
except KeyboardInterrupt as e:
  ircbot.disconnect("Shutdown initiated by Ctrl+C")
  dispatcher.shutdown()
  
except TronError as e:
  print e