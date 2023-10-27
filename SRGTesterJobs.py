import time
import telnetlib
import threading
from epics import caget

''''
Generate anonymous functions to complte jobs
Configures signalling between functions to schedule subtasks
'''


def GetPerformReadingJobs():
  # step 1: caput to EM1K0:GMD:GSR:1:ApplyZeroOffset
  # step 2: monitor EM1K0:GMD:GSR:1:GetRotSpeed for 30 seconds
  # step 3: concurrently monitor telnet logs
  # step 4: parse output of step 2; determine if failure, sort accordingling

  pub_zero = lambda : print("publishing a request to zero left unimplemented for now")
  read_hz = lambda: ReadBallHzForXSeconds(30)
  telnet_trace = lambda: print("not telnetting yet fam")
  eval_john = lambda: print("not implemented")
  return [pub_zero, read_hz, telnet_trace, eval_john]  # python lists suck, either use a dict or real queue or smthing


'''
Will return a list of samples of ball speed over a 30 second horizon
'''


def ReadBallHzForXSeconds(read_time):
  startTime = time.time()
  ret_list = []
  while ((time.time() - startTime) < read_time):
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
