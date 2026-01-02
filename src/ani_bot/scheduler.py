

import asyncio


class Task:
    def __init__(self, name):
        self.name = name

    def execute(self):
        print(f"Executing task: {self.name}")
        pass

class AsyncScheduler:
    def __init__(self):
        self.tasks = []

    async def _run_periodic(self, coro_func, interval):
        while True:
            await coro_func()          # 执行异步任务
            await asyncio.sleep(interval)

    def add_task(self, coro_func, interval):
        # 启动一个后台周期任务
        task = asyncio.create_task(self._run_periodic(coro_func, interval))
        self.tasks.append(task)

    async def run_task_now(self, coro_func):
        await coro_func()

    async def stop(self):
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        print("Scheduler stopped.")



scheduler = AsyncScheduler()


def run_scheduler():
    """
    启动调度器
    """
    scheduler.run()

def stop_scheduler():
    """
    停止调度器
    """
    scheduler.stop()


def restart_scheduler():
    """
    重启调度器
    """
    stop_scheduler()
    run_scheduler()

