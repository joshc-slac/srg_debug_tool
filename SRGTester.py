import threading
import time

from srg_tester_jobs import getperformreadingjobs
from request_server import request_server


class srg_tester:
  def __init__(self):
    self.cv = threading.condition()
    self.req_serv = request_server(self.cv)
    self.message_thread = threading.thread(target=self.mess_thread, args=(self.cv,))
    self.work_queue = []  # work queue of anonymous functions void(void)

    # pvs of interest:
    self.ballspeed_pv = "EM1K0:GMD:GSR:1:GetRotSpeed"

    self.do_work = False
    self.work_thread = threading.thread(target=self.work_thread, args=())

  '''
  the main work thread of the srgtester must to 4 things:
  1. inject epics layer request to "zero srg" i.e. publish
  2. monitor for x duration the value reported in the hz field
  3. grab and correlate telnet logs so we have "all bytes" on serial line
  4. mark success or failure of a given run
  '''
  def work_thread(self):
    while (1):
      if self.work_queue:
        job = self.work_queue.pop(0)
        print(f"starting job {job}")
        job()
        print(f"finished job {job}")

      else:
        time.sleep(2)

  '''
  todo: this should be protobuff'ed
  '''
  def mess_thread(self, cv):
    while (1):
      with cv:  # in python this also acquires lock
        cv.wait()
      mess = self.req_serv.get_message()
      if mess == "perform_reading":
        print("got message perform_reading")
        for job in getperformreadingjobs():
          self.work_queue.append(job)
      else:
        print(f"warning: do not know how to interpret message: {mess}")

  def start_work(self):
    self.do_work = True
    self.work_thread.start()
    self.message_thread.start()
    self.req_serv.start_work()


if __name__ == "__main__":
  t = srg_tester()
  # start tcp server
  t.start_work()
