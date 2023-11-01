from typing import Callable

from ..Task import Task, TaskState


class TestTask:
  def test_task_state_cycle(self):
      """
      Test TaskState lifecycle
      """
      call = lambda: True
      print(f"call is callable {isinstance(call, Callable)}")
      task = Task(task_name="test1",
                  work_function=call)
      assert task.get_state() == TaskState.NOT_STARTED
      task.start()
      assert task.get_state() == TaskState.RUNNING
      task.stop()
      assert task.get_state() == TaskState.COMPLETE

  def test_two(self):
    # While I have no love for meaningless commited code
    # Let this serve as an ugly reminder to actually enable these Tasks to communicate between
    # One another and to unit test that functionality here
    self.value = 2
    assert self.value == 2
