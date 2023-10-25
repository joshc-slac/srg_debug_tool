import threading
import time

import numpy as np
from epics import caget, caput

from SRGTesterJobs import GetPerformReadingJobs
from RequestServer import RequestServer

class SRGTester:
  def __init__(self):
    self.cv = threading.Condition()
    self.req_serv = RequestServer(self.cv)
    self.message_thread = threading.Thread(target= self.mess_thread, args=(self.cv,))
    self.work_queue = [] # work queue of anonymous functions void(void)

    #PVs of interest:
    self.ballspeed_pv = "EM1K0:GMD:GSR:1:GetRotSpeed"

    self.do_work = False
    self.work_thread = threading.Thread(target= self.work_thread, args=())

  '''
  The main work thread of the SRGTester must to 4 things:
  1. Inject EPICS layer request to "Zero SRG" i.e. publish 
  2. Monitor for X duration the value reported in the Hz field 
  3. Grab and correlate telnet logs so we have "all bytes" on serial line
  4. Mark success or failure of a given run
  '''
  def work_thread(self):
    while(1):
      if self.work_queue:
        job = self.work_queue.pop(0)
        print(f"Starting Job {job}")
        job()
        print(f"Finished Job {job}")

      else:
        time.sleep(2)

  '''
  Here we parse whatever byes we read off the TCP line and generate jobs to perform
  TODO: this should be protobuff'ed
  '''
  def mess_thread(self, cv):
    while(1):
      with cv: #in python this also acquires lock
        cv.wait()
      mess = self.req_serv.get_message()
      if mess == "PERFORM_READING":
        print("got message PERFORM_READING")
        for job in GetPerformReadingJobs():
          self.work_queue.append(job)
      else:
        print(f"WARNING: do not know how to interpret message: {mess}")

  def start_work(self):
    self.do_work = True
    self.work_thread.start()
    self.message_thread.start()
    self.req_serv.start_work()


  def get_ball_speed(self):
    print(caget(self.ballspeed_pv))

if __name__ == "__main__":
  t = SRGTester()
  # start TCP server
  t.start_work()
