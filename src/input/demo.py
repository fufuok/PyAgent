# -*- coding:utf-8 -*-
"""
    demo.py
    ~~~~~~~~
    示例数据收集插件

    :author: Fufu, 2021/6/7
"""
from random import randint, random

from . import InputPlugin


class Demo(InputPlugin):
    """示例数据收集插件"""

    # 模块名称
    name = 'demo'

    async def gather(self) -> None:
        """获取数据"""
        metric = self.metric({
            'x': randint(6, 30),
            'total': randint(1234, 9999999),
            'testin': randint(1234, 9999999),
            'test_float': random(),
            'demo_discard': '这个字段将最终被丢弃',
        })
        self.out_queue.put_nowait(metric)
