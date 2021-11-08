# -*- coding:utf-8 -*-
"""
    demo.py
    ~~~~~~~~
    示例数据收集插件

    :author: Fufu, 2021/6/7
"""
from asyncio import create_task, sleep
from random import randint

from . import InputPlugin


class Demo(InputPlugin):
    """示例数据收集插件"""

    # 模块名称
    name = 'demo'

    async def run(self) -> None:
        """定时执行收集"""
        while True:
            create_task(self.gather())
            await sleep(self.get_interval(60))

    async def gather(self) -> None:
        """获取数据"""
        metric = self.metric({
            'x': randint(6, 30),
            'total': randint(1234, 9999999),
            'testin': randint(1234, 9999999),
        })

        self.out_queue.put_nowait(metric)
