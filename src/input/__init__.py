# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~
    数据收集插件 input

    :author: Fufu, 2021/6/7
"""
import time
from asyncio import as_completed, create_task, sleep

from loguru import logger

from ..libs.plugin import BasePlugin


class InputPlugin(BasePlugin):
    """数据采集插件基类"""

    module = 'input'

    async def run(self):
        """定时执行收集"""
        logger.debug(f'{self.module}.{self.name} is working')
        while not self.is_closed():
            create_task(self.gather())
            await sleep(self.get_interval(60))

        logger.debug(f'{self.module}.{self.name} is closed')

    async def gather(self) -> None:
        """获取数据(默认需要上一次采集结束后才启动新的采集, 不允许堆叠)"""
        async with self.only_one() as ok:
            ok and await self.perf_gather()

    async def perf_gather(self) -> None:
        """Debug 运行时间"""
        start = time.perf_counter()
        logger.debug(f'gather {self.module}.{self.name} start')
        await self.run_gather()
        cost = time.perf_counter() - start
        logger.debug(f'gather {self.module}.{self.name} end, cost: {cost:.6}')

    async def run_gather(self):
        """执行采集"""
        pass

    async def run_tasks(self, tasks: list) -> None:
        """接收请求结果并推送"""
        for task in as_completed(tasks):
            metric = await task
            self.out_queue.put_nowait(metric)

    def is_closed(self):
        """检查当前插件是否该关闭 (名称不在开启的插件中)"""
        if self.name in self.conf.plugins_open:
            return False

        # 发送插件关闭信号 (特殊 Metric)
        self.out_queue.put_nowait(self.metric(None, tag='__CLOSE_SIGNAL__'))
        self.conf.plugins_working.discard(self.name)
        logger.info(f'Plugin {self.name} is closed')

        return True
