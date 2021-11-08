# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~
    数据处理插件 processor

    :author: Fufu, 2021/6/7
"""
from asyncio import Queue

from ..libs.metric import Metric
from ..libs.plugin import BasePlugin


class ProcessorPlugin(BasePlugin):
    """数据处理插件基类"""

    module = 'processor'

    # 使用中的公共插件
    common_plugins = {}

    def __init__(self, conf, in_queue: Queue, out_queue: Queue) -> None:
        super().__init__(conf)

        # 数据队列
        self.in_queue = in_queue
        self.out_queue = out_queue

    async def run(self) -> None:
        """数据处理"""
        while True:
            # 取队列数据
            metric = await self.in_queue.get()

            # 数据处理
            metric = await self.apply(metric)

            # 传递数据
            self.out_queue.put_nowait(metric)
            self.in_queue.task_done()

    async def apply(self, metric: Metric) -> Metric:
        """数据处理"""
        metric = await self.use_common_plugin(metric)
        return metric

    async def use_common_plugin(self, metric: Metric) -> Metric:
        """根据配置调用同模块插件"""
        for key, conf in self.get_plugin_conf_value().items():
            if key.startswith('use_plugin_'):
                plugin_name = key.split('use_plugin_', 1)[1]
                if not plugin_name:
                    continue

                plugin_cls = self.conf.get_plugin_obj('common', plugin_name)
                if not plugin_cls:
                    continue

                metric = await plugin_cls(self.conf, self.module, self.name, metric).run()

        return metric
