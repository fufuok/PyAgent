# -*- coding:utf-8 -*-
"""
    console.py
    ~~~~~~~~
    数据发布插件 - 输出到控制台

    :author: Fufu, 2021/6/7
"""
from . import OutputPlugin
from ..libs.metric import Metric


class Console(OutputPlugin):
    """数据发布 - 输出到控制台"""

    name = 'console'

    async def write(self, metric: Metric) -> None:
        """写入数据"""
        print('>>>', metric.as_text)
