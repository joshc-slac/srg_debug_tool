'''
Josh Cohen 2023 
A commdand generator file. Packages and sequences tasks for an owning class to execute in an anonymous job queue
'''


import time
import telnetlib
import threading
import typing

from epics import caget

from Task import Task


def get_perform_reading_jobs():
  ''''
  Generate anonymous functions to complte jobs
  Configures signalling between functions to schedule subtasks
  Returns a list of Tasks
  '''
  # step 1: caput to EM1K0:GMD:GSR:1:ApplyZeroOffset
  # step 2: monitor EM1K0:GMD:GSR:1:GetRotSpeed for 30 seconds
  # step 3: concurrently monitor telnet logs
  # step 4: parse output of step 2; determine if failure, sort accordingling

  pub_zero = Task("publish_zero",
                  lambda :
                    print("publishing a request to zero left unimplemented for now"))
  read_hz = Task("read_hz",
                 lambda:
                   read_ball_hz_for_x_seconds(30))
  telnet_trace = Task("telnet_trace",
                      lambda: 
                        print("not telnetting yet fam"))
  eval_run = Task("evaluate_run",
                  lambda: 
                    print("not implemented"))
  
  return [pub_zero, read_hz, telnet_trace, eval_run]  # python lists suck, either use a dict or real queue or smthing


def read_ball_hz_for_x_seconds(read_time=30.0, event_signal=threading.Event()):
  '''
  Description:
    Will return a list of samples of ball speed over a x second horizon
  Parameters:
    read_time: duration of read. if specified as < 0 will read indefinitely till event signal received
    event_signal: kill signal for read
  '''

  startTime = time.time()
  ret_list = []

  if (read_time > 0):
    should_read = lambda : (time.time() - startTime) < read_time
  else:
    should_read = lambda: True

  while (should_read() and not event_signal.is_set()):
    ret_list.append(caget("EM1K0:GMD:GSR:1:GetRotSpeed"))
    time.sleep(0.5)
  return ret_list


'''
- Acquires telnet connection to perform read
- Reads until kill signal excerices
Todo josh schedule this at the same time as the command to assert zero signal.
'''


def TelnetRead(ev, fname="sample.txt"):
  # cquire telnet
  with telnetlib.Telnet("ser-kfe-xgmd-01", 4012) as tn:
    # open a wel named file here
    f = open(f"{fname}", "w")
    while (ev.is_set() is not True):
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
  even = threading.Event()
  t1 = threading.Thread(target=TelnetRead, kwargs={"ev": even, "fname": "telnetlisten.txt"})
  t1.start()
  time.sleep(5)
  even.set()
  t1.join()
