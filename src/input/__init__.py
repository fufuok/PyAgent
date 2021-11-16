# -*- coding:utf-8 -*-
"""
    __init__.py
    ~~~~~~~~
    数据收集插件 input

    :author: Fufu, 2021/6/7
"""
from abc import abstractmethod
from asyncio import create_task, sleep
from typing import Any

from loguru import logger

from ..libs.plugin import BasePlugin


class InputPlugin(BasePlugin):
    """数据采集插件基类"""

    module = 'input'

    async def run(self):
        """定时执行收集"""
        logger.debug(f'{self.module}.{self.name} is working')
        while not self.is_closed():
            create_task(self.gather())
            await sleep(self.get_interval(60))

        logger.debug(f'{self.module}.{self.name} is closed')

    @abstractmethod
    async def gather(self) -> Any:
        """获取数据"""
        pass

    def is_closed(self):
        """检查当前插件是否该关闭 (名称不在开启的插件中)"""
        if self.name in self.conf.plugins_open:
            return False

        # 发送插件关闭信号 (特殊 Metric)
        self.out_queue.put_nowait(self.metric(None, tag='__CLOSE_SIGNAL__'))
        self.conf.plugins_working.discard(self.name)
        logger.info(f'Plugin {self.name} is closed')

        return True
