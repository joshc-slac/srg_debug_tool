import threading
from enum import IntEnum
from typing import Callable


class TaskState(IntEnum):
  NOT_STARTED = 0
  RUNNING = 1
  COMPLETE = 2
  FAILED = -1


class Task():
  '''
  Generic Task class
  '''
  def __init__(self, task_name: str, work_function: Callable[..., bool]) -> None:
    self.__state__ = TaskState.NOT_STARTED
    self.__task_name__ = task_name
    self.__work_function__ = work_function
    self.__work_thread__ = None

  def start(self) -> None:
    self.__work_thread__ = threading.Thread(target=self.__work_function__)  # TODO(josh): pass kwargs, likely cvs
    print(f"INFO: Starting job: {self.__task_name__}")
    self.__work_thread__.start()  # TODO (josh): wrap in try catch, return boolean based on success
    self.__state__ = TaskState.RUNNING  

  def stop(self) -> None:
    print(f"INFO: Stopping job: {self.__task_name__}")
    self.__work_thread__.join()  # TODO (josh): wrap in try catch (with timeout), return boolean based on success
    print(f"INFO: {self.__task_name__} joined")
    self.__state__ = TaskState.COMPLETE

  def get_state(self) -> TaskState:
    return self.__state__


if __name__ == "__main__":
  call = lambda: True
  task = Task(task_name="test1",
              work_function=call)
  task.start()
  task.stop()
