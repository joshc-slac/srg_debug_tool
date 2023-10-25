import time

from epics import caget

''''
Generate anonymous function to complte jobs
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
  return [pub_zero, read_hz, telnet_trace, eval_john] #python lists suck, either use a dict or real queue or smthing

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

if __name__ == '__main__':
  l = ReadBallHzForXSeconds(10)
  print(l)