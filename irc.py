import time
import nanotron
import threading
import irclib
import config

class IRCQueue(threading.Thread):
  def __init__(self, bot):
    self.bot = bot;
    self.lock = threading.Condition()
    self.shutdown = False
    self.queue = []
    threading.Thread.__init__(self)


  def run(self):
    while not self.shutdown or len(self.queue) > 0:
      self.lock.acquire()
      while len(self.queue) == 0 and not self.shutdown: self.lock.wait()
      if self.bot.connection.is_connected():
        func, args = self.queue.pop(0)
        func(*args)
      self.lock.release()
      time.sleep(1)


  def append(self, func, *args):
    self.lock.acquire()
    self.queue.append([func, args])
    self.lock.notify()
    self.lock.release()


  def drain(self):
    self.lock.acquire()
    self.shutdown = True
    self.lock.notify()
    self.lock.release()


class IRCBot(irclib.SimpleIRCClient):
  def __init__(self, dispatcher):
    irclib.SimpleIRCClient.__init__(self)
    self.dispatcher = dispatcher
    self.shutdown = False
    self.queue = IRCQueue(self)
    self.queue.start()
    self.cmdqueue = {}
    self.account = {}
    self.admins = self.readuserdb("admins.txt")
    self.users = self.readuserdb("users.txt")
    self.connection.add_global_handler("disconnect", self._on_disconnect, -10)
    self.connection.add_global_handler("kick", self._on_kick, -10)
    self.connection.add_global_handler("nick", self._on_nick, -10)
    self.connection.add_global_handler("part", self._on_part, -10)
    self.connection.add_global_handler("quit", self._on_quit, -10)
    self.connection.add_global_handler("ctcp", self._on_ctcp, -10)
    self.connection.add_global_handler("pubmsg", self._on_pubmsg, -10)
    self.connection.add_global_handler("privmsg", self._on_privmsg, -10)
    self.connection.add_global_handler("privnotice", self._on_privnotice, -10)
    self.connection.add_global_handler("320", self._on_whois_services, -10)
    self.connection.add_global_handler("endofwhois", self._on_endofwhois, -10)
    dispatcher.irc = self


  def _connect(self):
    while True:
      try:
        self.connect(config.IRC_SERVER, config.IRC_PORT, config.IRC_NICKNAME, None, ircname = config.IRC_REALNAME)
        break;
      except irclib.ServerConnectionError:
        time.sleep(5)


  def _on_disconnect(self, c, e):
    if not self.shutdown: self._connect()


  def _on_kick(self, c, e):
    self.account[e.arguments()[0]] = None
    if e.arguments()[0] == c.get_nickname() and e.target() == config.IRC_CHANNEL:
      self.queue.append(self.connection.privmsg, "ChanServ", "unban " + config.IRC_CHANNEL)
      self.queue.append(self.connection.join, config.IRC_CHANNEL)
      self.queue.append(self.connection.privmsg, config.IRC_CHANNEL, "Ouch, I don't like being kicked!")


  def _on_nick(self, c, e):
    self.account[irclib.nm_to_n(e.source())] = None


  def _on_part(self, c, e):
    self.account[irclib.nm_to_n(e.source())] = None


  def _on_quit(self, c, e):
    self.account[irclib.nm_to_n(e.source())] = None


  def disconnect(self, msg = "Shutting down..."):
    self.shutdown = True
    self.queue.drain()
    self.connection.disconnect(msg)


  def _on_ctcp(self, c, e):
    if e.arguments()[0] == "VERSION":
      self.queue.append(c.ctcp_reply, irclib.nm_to_n(e.source()), "VERSION NanotronIRC v0.1")
    elif e.arguments()[0] == "PING":
      if len(e.arguments()) > 1:
        self.queue.append(c.ctcp_reply, irclib.nm_to_n(e.source()), "PING " + e.arguments()[1])


  def _on_pubmsg(self, c, e):
    self.parsemessage(c, e, c.get_nickname() + ": !")


  def _on_privmsg(self, c, e):
    self.parsemessage(c, e, "!")


  def _on_privnotice(self, c, e):
    self.parsemessage(c, e, "!")


  def _on_whois_services(self, c, e):
    data = e.arguments()
    account = data[1].split("is signed on as account ", 1)
    if (len(account) == 2):
      account = account[1]
      nick = data[0]
      self.account[nick] = account
      for i in self.cmdqueue[nick]: self.execute(nick, account, i)
      self.cmdqueue[nick] = []


  def _on_endofwhois(self, c, e):
    if self.cmdqueue.get(e.arguments()[0], []) != []:
      print("Rejecting commands of \"%s\", because he is not authenticated:")
      print(self.cmdqueue[e.arguments()[0]])
      self.cmdqueue[e.arguments()[0]] = None


  def parsemessage(self, c, e, prefix):
    message = e.arguments()[0]
    if message[0:len(prefix)].lower() == prefix.lower():
      command = message[len(prefix):]
      nick = irclib.nm_to_n(e.source())
      account = self.account.get(nick, None)
      if account != None: self.execute(nick, account, command)
      else:
        if self.cmdqueue.get(nick, None) == None: self.cmdqueue[nick] = []
        self.cmdqueue[nick].append(command)
        self.queue.append(c.whois, [nick])


  def execute(self, nick, account, command):
    if self.users.get(account, None) == None and self.admins.get(account, None) == None:
      print("Rejected command from \"%s\", authenticated as \"%s\": (unknown account)" % (nick, account))
      print(command)
      return

    print("%s: %s" % (account, command))
    command = command.split(" ")

    if command[0].lower() == "appendjob":
      self.dispatcher.append(command[1:4])
      self.queue.append(self.connection.notice, nick, "Job has been enqueued")
      
    elif command[0].lower() == "prependjob":
      self.dispatcher.prepend(command[1:4])
      self.queue.append(self.connection.notice, nick, "Job has been enqueued")
      
    elif command[0].lower() == "killjob":
      result = self.dispatcher.kill(command[1:4])
      if result > 0:
        self.queue.append(self.connection.notice, nick,
                          ("%d addresses removed from %d jobs, %d of them were removed entirely, "
                         + "%d new jobs have spun off") % result)
      else: self.queue.append(self.connection.notice, nick, "Nothing matched")
      
    elif command[0].lower() == "admin" and self.admins.get(account, None) == True:
      self.admins[command[1]] = True
      self.writeuserdb("admins.txt", self.admins)
      self.queue.append(self.connection.notice, nick, "Granted admin privileges to \"%s\"" % command[1])
      
    elif command[0].lower() == "deadmin" and self.admins.get(account, None) == True:
      self.admins[command[1]] = None
      self.writeuserdb("admins.txt", self.admins)
      self.queue.append(self.connection.notice, nick, "Revoked admin privileges of \"%s\"" % command[1])
      
    elif command[0].lower() == "user" and self.admins.get(account, None) == True:
      self.users[command[1]] = True
      self.writeuserdb("users.txt", self.users)
      self.queue.append(self.connection.notice, nick, "Granted user privileges to \"%s\"" % command[1])
      
    elif command[0].lower() == "deuser" and self.admins.get(account, None) == True:
      self.users[command[1]] = None
      self.writeuserdb("users.txt", self.users)
      self.queue.append(self.connection.notice, nick, "Revoked user privileges of \"%s\"" % command[1])
      
    elif command[0].lower() == "shutdown" and self.admins.get(account, None) == True:
      print("Shutdown requested by \"%s\", authenticated as \"%s\"" % (nick, account))
      self.queue.append(self.connection.notice, nick, "Shutting down...")
      self.disconnect("Shutdown requested by \"%s\"" % nick)
      self.dispatcher.shutdown()

    else:
      self.queue.append(self.connection.notice, nick, "Unknown command \"%s\"" % command[0])


  def readuserdb(self, filename):
    file = open(filename, "r")
    data = {}
    for i in file:
      if len(i.strip()) > 0:
        data[i.strip()] = True
    file.close()
    return data


  def writeuserdb(self, filename, data):
    file = open(filename, "w")
    for i in data.keys():
      if data[i] == True:
        file.write("%s\n" % i)
    file.close()


  def log(self, message):
    self.queue.append(self.connection.privmsg, config.IRC_CHANNEL, message)

  def start(self):
    self._connect()
    password = raw_input("Enter your nanotron's IRC password (if it has one): ")
    self.queue.append(self.connection.privmsg, "NickServ", "ghost %s %s" % (config.IRC_NICKNAME, password))
    self.queue.append(self.connection.nick, config.IRC_NICKNAME)
    self.queue.append(self.connection.privmsg, "NickServ", "identify " + password)
    self.queue.append(self.connection.privmsg, "ChanServ", "unban " + config.IRC_CHANNEL)
    self.queue.append(self.connection.join, config.IRC_CHANNEL)
    self.queue.append(self.connection.privmsg, config.IRC_CHANNEL, "Nanotron starting up... (%s)" % config.IRC_IPODMODEL)
    irclib.SimpleIRCClient.start(self)
