# -*- coding:utf-8 -*-
"""
    default.py
    ~~~~~~~~
    默认数据发布插件

    :author: Fufu, 2021/6/7
"""
from . import OutputPlugin


class Default(OutputPlugin):
    """默认数据发布"""

    name = 'default'

    async def run(self) -> None:
        """数据打包并提交发布"""
        while True:
            # 消费队列数据
            metric = await self.in_queue.get()

            # 数据传递
            self.out_queue and self.out_queue.put_nowait(metric)
            self.in_queue.task_done()

    async def write(self, metrics):
        """写入数据"""
        pass
