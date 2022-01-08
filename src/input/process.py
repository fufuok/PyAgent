# -*- coding:utf-8 -*-
"""
    process.py
    ~~~~~~~~
    进程数据收集插件

    :author: Fufu, 2012/12/18
"""
from asyncio import create_task, sleep

from . import InputPlugin
from ..libs.helper import try_logger
from ..libs.psutil import get_process_info


class Process(InputPlugin):
    """进程数据收集插件"""

    # 模块名称
    name = 'process'

    async def run(self) -> None:
        """定时执行收集"""
        while True:
            create_task(self.gather())
            await sleep(self.get_interval(60))

    async def gather(self):
        await self.to_thread(self.get_process_info)

    @try_logger()
    def get_process_info(self):
        """采集进程概况"""
        pinfo_list = get_process_info(
            target=self.get_plugin_conf_value('target'),
            orderby=['cpu_percent', 'memory_percent'],
        )
        pinfo_list and self.out_queue.put_nowait(self.metric({
            "pinfo_list": pinfo_list,
        }))
