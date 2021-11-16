# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~
    数据发布插件 output

    :author: Fufu, 2021/6/7
"""
from typing import Any

from loguru import logger

from ..libs.metric import Metric
from ..libs.plugin import BasePlugin


class OutputPlugin(BasePlugin):
    """数据发布插件基类"""

    module = 'output'

    async def run(self) -> None:
        """数据打包并提交发布"""
        logger.debug(f'{self.module}.{self.name}({self.alias}) is working')
        is_closed = False
        while not is_closed:
            # 取队列数据
            metric = await self.in_queue.get()
            is_closed = metric.is_closed

            # 数据传递
            self.out_queue and self.out_queue.put_nowait(metric)

            await self.write(metric)
            self.in_queue.task_done()

        logger.debug(f'{self.module}.{self.name}({self.alias}) is closed')

    async def write(self, metric: Metric) -> Any:
        """写入数据"""
        pass
