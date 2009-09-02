import threading
import bruteforce

class Dispatcher(threading.Thread):
  def __init__(self, nanotron):
    self.nanotron = nanotron
    self.irc = None
    self.lock = threading.Condition()
    self.shuttingdown = False
    self.queue = []
    file = open("jobs.txt", "r")
    for i in file:
      if len(i.strip()) > 0:
        data = i.strip().split(" ")
        for i in range(3):
          data[i] = int(data[i], 16)
        self.queue.append(data)
    file.close()
    threading.Thread.__init__(self)


  def append(self, args):
    if len(args) != 3: args = [args[0], args[0], 1]
    for i in range(3):
      if isinstance(args[i], str):
        args[i] = int(args[i], 16)
    self.lock.acquire()
    self.queue.append(args)
    self.lock.notify()
    self.lock.release()
    self.savejobs()


  def prepend(self, args):
    if len(args) != 3: args = [args[0], args[0], 1]
    for i in range(3):
      if isinstance(args[i], str):
        args[i] = int(args[i], 16)
    self.lock.acquire()
    self.queue.insert(0, args)
    self.lock.notify()
    self.lock.release()
    self.savejobs()


  def kill(self, args):
    if len(args) != 3: args = [args[0], args[0], 1]
    for i in range(3):
      if isinstance(args[i], str):
        args[i] = int(args[i], 16)
    result = [0, 0, 0, 0]
    self.lock.acquire()
    newqueue = []
    for job in self.queue:
      astart = args[0] + ((((job[0] - args[0] - 1) // args[2]) + 1) * args[2] if job[0] > args[0] else 0)
      jstart = job[0] + ((((args[0] - job[0] - 1) // job[2]) + 1) * job[2] if args[0] > job[0] else 0)
      end = args[1] if args[1] < job[1] else job[1] + 1
      kickout = list(set(range(astart, end, args[2])) & set(range(jstart, end, job[2])))
      if len(kickout) > 0:
        kickout.sort()
        replace = []
        if kickout[0] != job[0]: replace.append([job[0], kickout[0] - job[2], job[2]])
        for j in range(len(kickout) - 1):
          if kickout[j] + job[2] != kickout[j + 1]:
            replace.append([kickout[j] + job[2], kickout[j + 1] - job[2], job[2]])
        if kickout[len(kickout) - 1] + job[2] <= job[1]:
          replace.append([kickout[len(kickout) - 1] + job[2], job[1], job[2]])
        newqueue.extend(replace)
        result[0] += len(kickout)
        result[1] += 1
        if len(replace) == 0: result[2] += 1
        else: result[3] += len(replace) - 1
      else: newqueue.append(job)
    self.queue = newqueue


    self.lock.notify()
    self.lock.release()
    self.savejobs()
    return tuple(result)


  def run(self):
    while not self.shuttingdown:
      self.lock.acquire()
      while len(self.queue) == 0 and not self.shuttingdown: self.lock.wait()
      if len(self.queue) > 0 and not self.shuttingdown:
        row = self.queue[0]
        addr = self.queue[0][0]
        self.lock.release()
        bruteforce.try_address(self.nanotron, addr, self.irc)
        self.lock.acquire()
        if row[0] == addr: row[0] += row[2]
        if row[0] > row[1]:
          try:
            self.queue.remove(row)
          except ValueError:
            pass
      self.lock.release()
      self.savejobs()


  def shutdown(self):
    self.shuttingdown = True
    self.lock.acquire()
    self.lock.notify()
    self.lock.release()
    self.join()
    sys.exit(0)


  def savejobs(self):
    self.lock.acquire()
    file = open("jobs.txt", "w")
    for i in self.queue:
      file.write("%x %x %x\n" % tuple(i))
    file.close()
    self.lock.release()

