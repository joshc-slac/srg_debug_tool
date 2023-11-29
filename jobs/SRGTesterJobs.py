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
from enum import IntEnum

from epics import caget, caput

from Task import Task


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
  PERFORM_UNARMED_READING = 0
  APPLY_ZERO_OFFSET = 1
  MONITOR_ROT_SPEED = 2
  MONITOR_SERIAL = 3
  EVALUATE_RUN = 4
  PERFORM_ARMED_READING = 5


def get_perform_reading_jobs(name_prefix: str = "test", job_type: SrgTesterJobType = SrgTesterJobType.PERFORM_UNARMED_READING):
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
                        read_ball_hz_for_x_seconds(read_time=10, fname=name_prefix, event_signal=ev_sig)))
  if (job_type is SrgTesterJobType.PERFORM_ARMED_READING):
    task_list.append(Task("publish_zero",
                     lambda : request_srg_zero()))
                          
  task_list.append(Task("evaluate_run",
                   lambda: 
                        evaluate_success(fname=name_prefix, event_signal=ev_sig)))
  
  return task_list  # python lists suck, either use a dict or real queue or smthing


def request_srg_zero():
  caput("EM1K0:GMD:GSR:1:ApplyZeroOffset", 1)
  return


def read_ball_hz_for_x_seconds(read_time=10.0, fname="sample", event_signal=threading.Event()):
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
      try:
        data = tn.read_some().decode("utf-8")
        # write data to file thusly:
        f.write(data)
      except UnicodeDecodeError as e:
        print(f"Ignoring UnicodeDecodeError: {e}")
        continue
    f.close()
  return


def evaluate_success(fname="sample", event_signal=threading.Event()):

  # wait for signal that read thread is complete
  event_signal.wait(None)
  print("begining analysis")

  # parse HZ output file to determine if we dropped the ball 
  # TODO(josh): double fileio is super inefecient, but python is annoying with mem. fix this
  # TODO(josh): wrap file io in try catch
  og_fname_hz = f"temp/{fname}_hz.csv"
  og_fname_telnet = f"temp/{fname}_telnet.txt"
  hz_arr = np.fromfile(og_fname_hz, dtype=float, count=-1, sep=",")
  fail_if_false = np.all(hz_arr)

  # sort files based on success or failure
  if fail_if_false is False:
    print("FIALLLL")
    os.replace(og_fname_hz, f"fail/{fname}_hz.csv")
    os.replace(og_fname_telnet, f"fail/{fname}_telnet.txt")
  else:
    print("SUCCC")
    os.replace(og_fname_hz, f"succ/{fname}_hz.csv")
    os.replace(og_fname_telnet, f"succ/{fname}_telnet.txt")

  return


if __name__ == '__main__':
  # even = threading.Event()
  jobs = get_perform_reading_jobs("your_sick")
  # naive task engine
  for job in jobs:
    job.start()

  for job in jobs:
    job.stop()

  print("done")
