#!/usr/bin/env python

import sys
import os
import nanotron
import irc
import dispatcher

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