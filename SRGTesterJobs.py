'''
Josh Cohen 2023 
A commdand generator file. Packages and sequences tasks for an owning class to execute in an anonymous job queue
'''


import time
import telnetlib
import threading
import typing
import os
import numpy as np

from epics import caget

from Task import Task


def get_perform_reading_jobs(name_prefix="test"):
  ''''
  Generate anonymous functions to complte jobs
  Configures signalling between functions to schedule subtasks
  Returns a list of Tasks
  '''
  # step 0: create tmp folder for file persistence
  # step 1: caput to EM1K0:GMD:GSR:1:ApplyZeroOffset
  # step 2: monitor EM1K0:GMD:GSR:1:GetRotSpeed for 30 seconds
  # step 3: concurrently monitor telnet logs
  # step 4: parse output of step 2; determine if failure, sort accordingling

  task_list = []
  ev_sig = threading.Event()  # TODO(josh): this should probably be passed to class so client can invoke kill signal

  # TODO(josh): make this a thing and not rely on the existence of this folder
  # task_list.append(Task("makefs",
  #                  lambda:
  #                       os.mkdir("temp")))
  task_list.append(Task("telnet_trace",
                   lambda: 
                        telnet_read(fname=name_prefix, event_signal=ev_sig)))
  task_list.append(Task("read_hz",
                   lambda:
                        read_ball_hz_for_x_seconds(read_time=30, fname=name_prefix, event_signal=ev_sig)))
  task_list.append(Task("publish_zero",
                   lambda :
                        print("publishing a request to zero left unimplemented for now")))
  task_list.append(Task("evaluate_run",
                   lambda: 
                        print("not implemented")))
  
  return task_list  # python lists suck, either use a dict or real queue or smthing


def read_ball_hz_for_x_seconds(read_time=10.0, fname="tmp", event_signal=threading.Event()):
  '''
  Description:
    Will return a list of samples of ball speed over a x second horizon
  Parameters:
    read_time: duration of read. if specified as < 0 will read indefinitely till event signal received
    event_signal: kill signal for read
  '''

  startTime = time.time()
  ret_list = np.zeros((int(read_time) * 1000))  # TODO(josh): address hardcoded value, maybe correlate to sleep rate limiter
  idx = 0

  print(f"shape is: {ret_list.shape}")

  # TODO(josh): incorporate kill signal here
  if (read_time > 0):
    should_read = lambda : ((time.time() - startTime) < read_time) and event_signal.is_set() is not True
  else:
    should_read = lambda: event_signal.is_set() is not True

  while (should_read()):
    val = caget("EM1K0:GMD:GSR:1:GetRotSpeed")
    ret_list[idx] = val
    idx += 1
    time.sleep(0.1)

  ret_list = ret_list[:idx]
  print(ret_list.shape)
  ret_list.tofile(f"temp/{fname}_hz.csv", sep=",")
  event_signal.set()  # TODO(josh): this is too buried for my liking, preferably make a timer task that produces the kill signal for these thredas to kill
  return ret_list


'''
- Acquires telnet connection to perform read
- Reads until kill signal excerices
Todo josh schedule this at the same time as the command to assert zero signal.
'''


def telnet_read(fname="sample", event_signal=threading.Event()):
  # cquire telnet
  with telnetlib.Telnet("ser-kfe-xgmd-01", 4012) as tn:
    # open a wel named file here
    f = open(f"temp/{fname}_telnet.txt", "w")
    while (event_signal.is_set() is not True):
      print("working on it...")
      try:
        data = tn.read_some().decode("utf-8")
        # write data to file thusly:
        f.write(data)
      except UnicodeDecodeError as e:
        print(f"Ignoring UnicodeDecodeError: {e}")
        continue
    f.close()
  return


if __name__ == '__main__':
  # even = threading.Event()
  jobs = get_perform_reading_jobs("your_sick")
  for job in jobs:
    job.start()

  for job in jobs:
    job.stop()

  print("done")
