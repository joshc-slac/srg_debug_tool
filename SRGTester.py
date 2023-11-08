import threading
import time
from datetime import datetime

from SRGTesterJobs import SrgTesterJobType, get_perform_reading_jobs
from RequestServer import RequestServer


class SrgTester:
  def __init__(self):
    self.cv = threading.Condition()
    self.req_serv = RequestServer(self.cv)
    self.message_thread = threading.Thread(target=self.mess_thread, args=(self.cv,))
    self.work_queue = []  # work queue of anonymous functions void(void) #TODO make this of type queue from the queue lib

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
        # task.stop()  # TODO(josh): async-ify the tasks. Requires either unifying Condition, Event, or notion of [.follows() and .is_ready()], 
        # determine what it means for a thread to rejoin in this context? after we do a high level command send join command to all child threads?

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
      mess = SrgTesterJobType(int(self.req_serv.get_message()))  # TODO(josh): unpacking int thing sucks but so does python 3.6
      print(f"lookuing at mess: {mess}, {type(mess)}")
      print(f"is mess PERFORM_UNARMED_READING? {mess is SrgTesterJobType.PERFORM_UNARMED_READING}")
      # server side arg validation
      if (mess is not SrgTesterJobType.PERFORM_UNARMED_READING and mess is not SrgTesterJobType.PERFORM_ARMED_READING):
        print(f"Error: do not know how to interpret message: {mess}")
        continue
      else:
        print(f"Info: got message {mess}")
        # generate unique filename... # TODO(josh): itd be slightly more intelligent for the client to opine o fname
        fname_time = datetime.now().strftime("%m_%d_%Y-%H_%M_%S")
        for job in get_perform_reading_jobs(fname_time, mess):
          self.work_queue.append(job)

  def start_work(self):
    self.do_work = True
    self.work_thread.start()
    self.message_thread.start()
    self.req_serv.start_work()


if __name__ == "__main__":
  t = SrgTester()
  # start tcp server
  t.start_work()
