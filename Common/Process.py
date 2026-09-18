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
        if task is None:
            print(f"{proc_name}(PID:{pid}) 收到退出信号，停止工作")
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


@singleton
class ProcessManager:
    task_queue = multiprocessing.Queue()
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
        '''
        必须在__main__内调用
        '''
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
