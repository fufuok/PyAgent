# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~
    数据处理插件 processor

    :author: Fufu, 2021/6/7
"""
from loguru import logger

from ..libs.metric import Metric
from ..libs.plugin import BasePlugin


class ProcessorPlugin(BasePlugin):
    """数据处理插件基类"""

    module = 'processor'

    # 使用中的公共插件
    common_plugins = {}

    async def run(self) -> None:
        """数据处理"""
        logger.debug(f'{self.module}.{self.name}({self.alias}) is working')
        is_closed = False
        while not is_closed:
            # 取队列数据
            metric = await self.in_queue.get()
            is_closed = metric.is_closed

            # 数据处理
            metric = await self.apply(metric)

            # 传递数据
            self.out_queue.put_nowait(metric)
            self.in_queue.task_done()

        logger.debug(f'{self.module}.{self.name}({self.alias}) is closed')

    async def apply(self, metric: Metric) -> Metric:
        """数据处理"""
        return await self.use_common_plugin(metric)
