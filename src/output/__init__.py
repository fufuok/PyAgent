# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~
    数据发布插件 output

    :author: Fufu, 2021/6/7
"""
from abc import abstractmethod
from asyncio import Queue
from typing import Any, Optional

from ..libs.metric import Metric
from ..libs.plugin import BasePlugin


class OutputPlugin(BasePlugin):
    """数据发布插件基类"""

    module = 'output'

    def __init__(self, conf, in_queue: Queue, out_queue: Optional[Queue]) -> None:
        super().__init__(conf)

        # 数据队列
        self.in_queue = in_queue
        self.out_queue = out_queue

    async def run(self) -> None:
        """数据打包并提交发布"""
        while True:
            # 取队列数据
            metric = await self.in_queue.get()

            # 数据传递
            self.out_queue and self.out_queue.put_nowait(metric)

            await self.write(metric)
            self.in_queue.task_done()

    @abstractmethod
    async def write(self, metric: Metric) -> Any:
        """写入数据"""
        pass
