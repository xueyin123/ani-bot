

import asyncio
from typing import Any, Callable, Coroutine

class AsyncScheduler:
    def __init__(self):
        self.tasks = []
        self._running = False

    async def _run_periodic(self, coro_func: Callable[[], Coroutine[Any, Any, Any]], interval: float):
        try:
            while self._running:
                await coro_func()
                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            # 任务被取消时的清理逻辑
            print(f"Task {coro_func.__name__} cancelled")
            raise

    def add_task(self, coro_func: Callable[[], Coroutine[Any, Any, Any]], interval: float):
        # 启动一个后台周期任务
        task = asyncio.create_task(self._run_periodic(coro_func, interval))
        self.tasks.append(task)

    async def start(self):
        """启动调度器"""
        self._running = True
        print("Scheduler started.")

    async def stop(self):
        """优雅停止调度器"""
        self._running = False
        for task in self.tasks:
            task.cancel()
        # 修复：需要 await asyncio.gather
        await asyncio.gather(*self.tasks, return_exceptions=True)
        print("Scheduler stopped.")

