import multiprocessing
from queue import Empty as multiprocessing_Empty
import os

from Common.Common import *
from Pattern.singleton import *


def worker(
    task_queue,
    result_queue=None,
):
    """
    不断从队列获取任务并执行
    """
    proc_name = multiprocessing.current_process().name
    pid = os.getpid()
    while True:
        try:
            task = task_queue.get()
        except multiprocessing_Empty:
            continue
        try:
            if task is None:
                print(f"{proc_name}(PID:{pid}) 收到退出信号，停止工作\n")
                break

            func, args, kwargs = task
            try:
                print(f"{proc_name} start task {task}")
                result = func(*args, **kwargs)
                if result_queue:
                    result_queue.put(result)
                print(f"{proc_name} end task {task}")
            except Exception as e:
                print(f"{proc_name} task {task} error {e}")
        finally:
            task_queue.task_done()  # ← 每个任务处理完（成功/失败/退出信号）都要调用


@singleton
class ProcessManager:
    task_queue = multiprocessing.JoinableQueue()
    result_queue = multiprocessing.Queue()
    num_workers = 0
    workers = []
    __started = False

    def __del__(self):
        for _ in range(self.num_workers):
            self.task_queue.put(None)
        for p in self.workers:
            p.join()

    def StartWorkers(self, num_workers=1):
        """
        必须在__main__内调用
        """
        if self.__started:
            return
        self.__started = True

        self.num_workers = num_workers
        for _ in range(num_workers):
            p = multiprocessing.Process(
                target=worker, args=(self.task_queue, self.result_queue)
            )
            p.daemon = True
            p.start()

            self.workers.append(p)

    def AddTask(self, func, *args, **kwargs):
        self.task_queue.put((func, args, kwargs))

    def WaitAll(self):
        """
        阻塞直到当前 task_queue 中所有已加入的任务全部处理完成。
        不会退出/关闭 worker，之后仍可继续 AddTask。
        """
        self.task_queue.join()

    def WaitAllWithTimeout(self, timeout=None):
        """
        带超时的版本。返回 True 表示全部完成，False 表示超时。
        注意：超时后 join() 已经在后台线程里跑完了才能这么判断，
        若想严格超时，请用下面的轮询方式。
        """
        import time

        deadline = None if timeout is None else time.time() + timeout
        while True:
            # unfinished_tasks 是 JoinableQueue 内部计数器
            if self.task_queue._unfinished_tasks._semlock._is_zero():
                return True
            if deadline is not None and time.time() > deadline:
                return False
            time.sleep(0.01)
