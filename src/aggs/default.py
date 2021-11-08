# -*- coding:utf-8 -*-
"""
    default.py
    ~~~~~~~~
    默认数据汇聚/报警插件

    :author: Fufu, 2021/6/7
"""
from . import AggsPlugin
from ..libs.metric import Metric


class Default(AggsPlugin):
    """默认数据汇聚/报警"""

    name = 'default'

    async def run(self) -> None:
        """数据汇聚/报警"""
        while True:
            # 取队列数据
            metric = await self.in_queue.get()

            # 传递数据
            self.out_queue.put_nowait(metric)
            self.in_queue.task_done()

    async def alarm(self, metric: Metric) -> None:
        """报警"""
        pass
