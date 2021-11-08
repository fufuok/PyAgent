# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~
    数据收集插件 input

    :author: Fufu, 2021/6/7
"""
from abc import abstractmethod
from asyncio import Queue
from typing import Any

from ..libs.plugin import BasePlugin


class InputPlugin(BasePlugin):
    """数据采集插件基类"""

    module = 'input'

    def __init__(self, conf: Any, out_queue: Queue) -> None:
        super().__init__(conf)

        # 数据队列
        self.out_queue = out_queue

    @abstractmethod
    async def gather(self) -> Any:
        """获取数据"""
        pass
