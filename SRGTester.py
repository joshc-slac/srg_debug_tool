import threading
import time
from enum import IntEnum

from SRGTesterJobs import get_perform_reading_jobs
from RequestServer import RequestServer


class SrgTesterJobType(IntEnum):
  # TODO(josh): can reasonably be split into its own file
  # TODO(josh): get StrEnum to work on prod machines... needs pip-ability
  NONE = -1
  '''
  # High Level Command: Perform Reading
  step 1: caput to EM1K0:GMD:GSR:1:ApplyZeroOffset
  step 2: monitor EM1K0:GMD:GSR:1:GetRotSpeed for 30 seconds
  step 3: concurrently monitor telnet logs
  step 4: parse output of step 2; determine if failure, sort accordingling 
  '''
  PERFORM_READING = 0
  APPLY_ZERO_OFFSET = 1
  MONITOR_ROT_SPEED = 2
  MONITOR_SERIAL = 3
  EVALUATE_RUN = 4


class SrgTester:
  def __init__(self):
    self.cv = threading.Condition()
    self.req_serv = RequestServer(self.cv)
    self.message_thread = threading.Thread(target=self.mess_thread, args=(self.cv,))
    self.work_queue = []  # work queue of anonymous functions void(void)

    self.do_work = False
    self.work_thread = threading.Thread(target=self.work_thread, args=())

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
        task = self.work_queue.pop(0)
        task.start()
        task.stop()  # TODO(josh): async-ify the tasks. Requires either unifying Condition, Event, or notion of [.follows() and .is_ready()]

      else:
        time.sleep(2)

  '''
  Parse contents of message, when applicable append to job queue
  todo: this should be protobuff'ed
  '''
  def mess_thread(self, cv):
    while (1):
      with cv:  # in python this also acquires lock
        cv.wait()
      mess = self.req_serv.get_message()
      if int(mess) == SrgTesterJobType.PERFORM_READING:
        print(f"got message {SrgTesterJobType.PERFORM_READING}")
        for job in get_perform_reading_jobs():
          self.work_queue.append(job)
      else:
        print(f"warning: do not know how to interpret message: {mess}")

  def start_work(self):
    self.do_work = True
    self.work_thread.start()
    self.message_thread.start()
    self.req_serv.start_work()


if __name__ == "__main__":
  t = SrgTester()
  # start tcp server
  t.start_work()
